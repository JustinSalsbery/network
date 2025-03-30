
from io import TextIOWrapper

from src.components import _comps, _ServiceType, _Service, _IfaceConfig
from src.components import *


_SPACE = "  "

class Configurator():
    def __init__(self):
        """
        Write out the configuration as `docker-compose.yml`.
        MUST be called for the configuration to be created.
        """

        with open("docker-compose.yml", "w") as file:
            self.__write_services(file)

            # docker compose will fail unless networks follow after services
            self.__write_inets(file)

    def __write_services(self, file: TextIOWrapper):
        file.write("services:\n")

        # write servers

        server = []
        if _ServiceType.server.name in _comps:
            servers = _comps[_ServiceType.server.name]

        for server in servers:
            assert(type(server) == Server)
            self.__write_service(file, server)

        # write traffic generators

        tgens = []
        if _ServiceType.traffic_generator.name in _comps:
            tgens = _comps[_ServiceType.traffic_generator.name]

        for tgen in tgens:
            assert(type(tgen) == TrafficGenerator)
            self.__write_service(file, tgen)

            file.write(f"{_SPACE * 3}# Locust configuration:\n")
            file.write(f"{_SPACE * 3}DST_IP: {tgen._dst_ip}\n")
            file.write(f"{_SPACE * 3}CONN_MAX: {tgen._conn_max}\n")
            file.write(f"{_SPACE * 3}CONN_RATE: {tgen._conn_rate}\n")
            file.write(f"{_SPACE * 3}PROTO: {tgen._proto}\n")
            file.write(f"{_SPACE * 3}PAGES: {" ".join(tgen._pages)}\n")
            file.write(f"{_SPACE * 3}WAIT_MIN: {tgen._wait_min}\n")
            file.write(f"{_SPACE * 3}WAIT_MAX: {tgen._wait_max}\n")

    def __write_service(self, file: TextIOWrapper, service: _Service):
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
        file.write(f"{_SPACE * 3}- NET_ADMIN\n")
        file.write(f"{_SPACE * 2}environment:\n")
        file.write(f"{_SPACE * 3}# Interface configurations:\n")

        ifaces = []
        src_ips = []
        net_masks = []
        gateways = []

        for iface in service._ifaces:
            assert(type(iface) == _IfaceConfig)

            ifaces.append(iface._iface._name)
            src_ips.append(iface._src_ip)
            net_masks.append(iface._iface._net_mask)
            gateways.append(str(iface._gateway))  # gateway may be NoneType

        file.write(f"{_SPACE * 3}IFACES: {" ".join(ifaces)}\n")
        file.write(f"{_SPACE * 3}SRC_IPS: {" ".join(src_ips)}\n")
        file.write(f"{_SPACE * 3}NET_MASKS: {" ".join(net_masks)}\n")
        file.write(f"{_SPACE * 3}GATEWAYS: {" ".join(gateways)}\n")

    def __write_inets(self, file: TextIOWrapper):
        file.write("networks:\n")

        ifaces = _comps["Iface"]
        for iface in ifaces:
            assert(type(iface) == Iface)

            file.write(f"{_SPACE * 1}{iface._name}:\n")
            file.write(f"{_SPACE * 2}name: {iface._name}\n")
            file.write(f"{_SPACE * 2}driver: bridge\n")
            file.write(f"{_SPACE * 2}internal: true\n")
            file.write(f"{_SPACE * 2}driver_opts: # os defines a suffix\n")
            file.write(f"{_SPACE * 3}com.docker.network.container_iface_prefix: {iface._name}_\n")
