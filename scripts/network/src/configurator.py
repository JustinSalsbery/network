
from io import TextIOWrapper

from src.components import _comps, _ServiceType, _Service, _IfaceConfig, _IPv4
from src.components import *


_SPACE = "  "

class Configurator():
    def __init__(self):
        """
        Write out the configuration as `docker-compose.yml`.
        MUST be called for the configuration to be created.
        """

        # By default, Docker only supports around 30 network interfaces.
        # By writing a (temporary) subnet in the Docker Compose file, we can exceed this limitation.
        
        self.__ip = 0x0a000000  # 10.0.0.0/8
        self.__prefix_len = 22  # 10.0.0.0/22 -> 10.0.1.0/22 ...

        # Enables 2 ** 14 interfaces with 2 ** 10 services per interface.

        with open("docker-compose.yml", "w") as file:
            self.__write_services(file)

            # docker compose will fail unless networks follow after services
            self.__write_inets(file)

    def __write_services(self, file: TextIOWrapper):
        """
        @params:
            - file: File to write to.
        """

        file.write("services:\n")

        # write servers

        servers = []
        if _ServiceType.server.name in _comps:
            servers = _comps[_ServiceType.server.name]

        for server in servers:
            assert(type(server) == Server)
            self.__write_service(file, server)

        # write clients

        clients = []
        if _ServiceType.client.name in _comps:
            clients = _comps[_ServiceType.client.name]

        for client in clients:
            assert(type(client) == Client)
            self.__write_service(file, client)

        # write traffic generators

        tgens = []
        if _ServiceType.tgen.name in _comps:
            tgens = _comps[_ServiceType.tgen.name]

        for tgen in tgens:
            assert(type(tgen) == TrafficGenerator)
            self.__write_service(file, tgen)

            file.write(f"{_SPACE * 3}# Locust configuration:\n")
            file.write(f"{_SPACE * 3}DST_IP: {tgen._dst_ip._ip_str}\n")
            file.write(f"{_SPACE * 3}CONN_MAX: {tgen._conn_max}\n")
            file.write(f"{_SPACE * 3}CONN_RATE: {tgen._conn_rate}\n")
            file.write(f"{_SPACE * 3}PROTO: {tgen._proto}\n")
            file.write(f"{_SPACE * 3}PAGES: {" ".join(tgen._pages)}\n")
            file.write(f"{_SPACE * 3}WAIT_MIN: {tgen._wait_min}\n")
            file.write(f"{_SPACE * 3}WAIT_MAX: {tgen._wait_max}\n")

        # write routers

        routers = []
        if _ServiceType.router.name in _comps:
            routers = _comps[_ServiceType.router.name]

        for router in routers:
            assert(type(router) == Router)
            self.__write_service(file, router)

            file.write(f"{_SPACE * 3}# Router configuration:\n")
            file.write(f"{_SPACE * 3}ECMP: {str(router._ecmp).lower()}\n")

            visibilities = []
            nats = []

            for iface in router._ifaces:
                assert(type(iface) == _IfaceConfig)

                visibilities.append(iface._iface._cidr._subnet_type.name)
                nats.append(iface._nat.name)

            file.write(f"{_SPACE * 3}VISIBILITIES: {" ".join(visibilities)}\n")
            file.write(f"{_SPACE * 3}NATS: {" ".join(nats)}\n")

    def __write_service(self, file: TextIOWrapper, service: _Service):
        """
        @params:
            - file: File to write to.
            - service: Service configuration to write.
        """

        file.write(f"{_SPACE * 1}{service._name}:\n")
        file.write(f"{_SPACE * 2}container_name: {service._name}\n")
        file.write(f"{_SPACE * 2}image: {service._image}\n")
        file.write(f"{_SPACE * 2}restart: unless-stopped\n")
        file.write(f"{_SPACE * 2}deploy:\n")
        file.write(f"{_SPACE * 3}resources:\n")
        file.write(f"{_SPACE * 4}limits:\n")
        file.write(f"{_SPACE * 5}cpus: {service._cpu_limit}\n")
        file.write(f"{_SPACE * 5}memory: {service._mem_limit}\n")

        if service._disable_swap:
            file.write(f"{_SPACE * 2}memswap_limit: {service._mem_limit}\n")

        file.write(f"{_SPACE * 2}volumes:\n")
        file.write(f"{_SPACE * 3}- ./shared:/app/shared\n")
        file.write(f"{_SPACE * 2}networks:\n")

        for iface in service._ifaces:
            assert(type(iface) == _IfaceConfig)
            file.write(f"{_SPACE * 3}- {iface._iface._name}\n")

        file.write(f"{_SPACE * 2}cap_add:\n")
        file.write(f"{_SPACE * 3}- NET_ADMIN # enables ifconfig, route\n")
        file.write(f"{_SPACE * 2}privileged: true # enables sysctl\n")
        file.write(f"{_SPACE * 2}environment:\n")
        file.write(f"{_SPACE * 3}# Interface configurations:\n")
        file.write(f"{_SPACE * 3}FORWARD: {str(service._forward).lower()}\n")

        ifaces = []
        src_ips = []
        net_masks = []
        gateways = []
        firewalls = []

        for iface in service._ifaces:
            assert(type(iface) == _IfaceConfig)

            ifaces.append(iface._iface._name)
            src_ips.append(iface._src._ip_str)
            net_masks.append(iface._iface._cidr._netmask._ip_str)
            gateways.append(iface._gateway._ip_str)
            firewalls.append(iface._firewall.name)

        file.write(f"{_SPACE * 3}IFACES: {" ".join(ifaces)}\n")
        file.write(f"{_SPACE * 3}SRC_IPS: {" ".join(src_ips)}\n")
        file.write(f"{_SPACE * 3}NET_MASKS: {" ".join(net_masks)}\n")
        file.write(f"{_SPACE * 3}GATEWAYS: {" ".join(gateways)}\n")
        file.write(f"{_SPACE * 3}FIREWALLS: {" ".join(firewalls)}\n")

    def __write_inets(self, file: TextIOWrapper):
        """
        @params:
            - file: File to write to.
        """

        file.write("networks:\n")

        ifaces = _comps["Iface"]
        for iface in ifaces:
            assert(type(iface) == Iface)

            file.write(f"{_SPACE * 1}{iface._name}:\n")
            file.write(f"{_SPACE * 2}name: {iface._name}\n")
            file.write(f"{_SPACE * 2}driver: bridge\n")
            file.write(f"{_SPACE * 2}internal: true\n")
            file.write(f"{_SPACE * 2}ipam:\n")
            file.write(f"{_SPACE * 3}config: # this is a workaround for a docker limitation\n")
            file.write(f"{_SPACE * 4}- subnet: {self.__get_cidr()} # temporary subnet\n")
            file.write(f"{_SPACE * 2}driver_opts: # os defines a suffix\n")
            file.write(f"{_SPACE * 3}com.docker.network.container_iface_prefix: {iface._name}_\n")

    def __get_cidr(self) -> str:
        """
        @returns: An IPv4 address in CIDR notation.
        """

        suffix = 32 - self.__prefix_len

        self.__ip += 2 ** suffix
        if self.__ip >= 0x0b000000: # 11.0.0.0
            print("error: Alloted subnet (10.0.0.0/8) exceeded.")
            print("\tConsider changing settings in the Configurator.")
            exit(1)

        ip = _IPv4(self.__ip)
        return f"{ip._ip_str}/{self.__prefix_len}"
