
from io import TextIOWrapper

from src.components import _comps, _ServiceType, _Service, _IfaceConfig, _IPv4, _CIDR
from src.components import *


_SPACE = "  "

class Configurator():
    def __init__(self, available_range: str = "10.0.0.0/8", prefix_len: int = 22):
        """
        Write out the configuration as `docker-compose.yml`.
        @params:
            - available_range: The available IP range in CIDR notation for creating Docker subnets.
            - prefix_len: The size of each subnet.
        WARNING:
            - The configurator MUST be called for the configuration to be created.
            - By default, Docker only supports around 30 network interfaces.
              By writing subnets in the Docker Compose file we can exceed this limitation.
              The containers do not use the subnet.
            - Docker will create an externally accessable gateway at the .1 of each subnet; 
              ex. 10.0.0.1 and 10.0.4.1. These gateways may interfere with the host's networking.
              Other containers (.2, .3, etc) will not be externally accessible.
        """
        
        self.__cidr = _CIDR(available_range)
        self.__ip = self.__cidr._ip._int

        suffix = 32 - self.__cidr._prefix_len
        self.__ip_max = self.__ip + 2 ** suffix

        self.__prefix_len = prefix_len

        with open("docker-compose.yml", "w") as file:

            # docker compose down will fail unless networks follow after services
            self.__write_services(file)
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
            file.write(f"{_SPACE * 3}DST_IP: {tgen._dst_ip._str}\n")
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

            cidrs = []
            visibilities = []
            nats = []

            for config in router._iface_configs:
                assert(type(config) == _IfaceConfig)

                cidrs.append(config._iface._cidr._str)
                visibilities.append(config._iface._cidr._visibility.name)
                nats.append(config._nat.name)

            file.write(f"{_SPACE * 3}CIDRS: {" ".join(cidrs)}\n")
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

        for config in service._iface_configs:
            assert(type(config) == _IfaceConfig)
            file.write(f"{_SPACE * 3}- {config._iface._name}\n")

        file.write(f"{_SPACE * 2}cap_add:\n")
        file.write(f"{_SPACE * 3}- NET_ADMIN # enables ifconfig, route\n")
        file.write(f"{_SPACE * 2}privileged: true # enables sysctl\n")
        file.write(f"{_SPACE * 2}environment:\n")
        file.write(f"{_SPACE * 3}# Interface configurations:\n")
        file.write(f"{_SPACE * 3}FORWARD: {str(service._forward).lower()}\n")
        file.write(f"{_SPACE * 3}SYN_COOKIE: {service._syn_cookie.name}\n")
        file.write(f"{_SPACE * 3}CONGESTION_CONTROL: {service._congestion_control.name}\n")

        ifaces = []
        src_ips = []
        net_masks = []
        gateways = []
        firewalls = []
        drop_percents = []
        delays = []

        for config in service._iface_configs:
            assert(type(config) == _IfaceConfig)

            ifaces.append(config._iface._name)
            src_ips.append(config._src._str)
            net_masks.append(config._iface._cidr._netmask._str)
            gateways.append(config._gateway._str)
            firewalls.append(config._firewall.name)
            drop_percents.append(f"{config._drop_percent}")
            delays.append(f"{config._delay}")

        file.write(f"{_SPACE * 3}IFACES: {" ".join(ifaces)}\n")
        file.write(f"{_SPACE * 3}SRC_IPS: {" ".join(src_ips)}\n")
        file.write(f"{_SPACE * 3}NET_MASKS: {" ".join(net_masks)}\n")
        file.write(f"{_SPACE * 3}GATEWAYS: {" ".join(gateways)}\n")
        file.write(f"{_SPACE * 3}FIREWALLS: {" ".join(firewalls)}\n")
        file.write(f"{_SPACE * 3}DROP_PERCENTS: {" ".join(drop_percents)}\n")
        file.write(f"{_SPACE * 3}DELAYS: {" ".join(delays)}\n")

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

        if self.__ip >= self.__ip_max:
            print(f"error: Allocated subnet {self.__cidr._str} exceeded.")
            print("\tConsider changing settings for the Configurator.")
            exit(1)

        ip = _IPv4(self.__ip)
        cidr = f"{ip._str}/{self.__prefix_len}"

        suffix = 32 - self.__prefix_len
        self.__ip += 2 ** suffix  # iterate

        return cidr
