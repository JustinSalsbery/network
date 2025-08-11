
from io import TextIOWrapper
from traceback import print_stack

from src.components import *  # private must be imported manually
from src.components import _comps, _ServiceType, _Service, _IfaceConfig, _IPv4, _CIDR, _Domain
from src.grapher import Grapher


_SPACE = "  "

class Configurator():
    def __init__(self, available_range: str = "10.0.0.0/8", prefix_len: int = 22, 
                 color: bool = True, extra: bool = False):
        """
        Outputs the configuration as `docker-compose.yml`.
        @params:
            - available_range: The available IP range in CIDR notation for creating temporary subnets.
            - prefix_len: The size of each temporary subnet.
            - color: Enables or disables color in the graph.
            - extra: Enables or disables extra information in the graph.
        Note:
            - The configurator MUST be called for the configuration to be created.
            - By default, Docker only supports around 30 network interfaces.
              By writing temporary subnets in the Docker Compose file we can exceed this limitation.
              The containers do not use these temporary subnets.
            - Docker will create a gateway at the .1 of each subnet; ex. 10.0.0.1 and 10.0.4.1.
              These gateways are internally and externally accessible and may interfere with 
              both container networking and host networking.
            - The available range MUST NOT overlap with any IPs in the configuration.
        """
        
        self.__cidr = _CIDR(available_range)
        self.__ip = self.__cidr._ip._int

        suffix_len = 32 - self.__cidr._prefix_len
        self.__ip_max = self.__ip + 2 ** suffix_len

        self.__prefix_len = prefix_len

        with open("docker-compose.yml", "w") as file:

            # docker compose down will fail unless networks follow after services
            self.__write_services(file)
            self.__write_inets(file)

        Grapher(color, extra)

    def __write_services(self, file: TextIOWrapper):
        """
        @params:
            - file: File to write to.
        """

        file.write("services:\n")

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
            file.write(f"{_SPACE * 3}TARGET: {tgen._target}\n")
            file.write(f"{_SPACE * 3}CONN_MAX: {tgen._conn_max}\n")
            file.write(f"{_SPACE * 3}CONN_RATE: {tgen._conn_rate}\n")
            file.write(f"{_SPACE * 3}CONN_DUR: {tgen._conn_dur}\n")
            file.write(f"{_SPACE * 3}PROTO: {tgen._proto.name}\n")
            file.write(f"{_SPACE * 3}REQUESTS: {" ".join(tgen._requests)}\n")
            file.write(f"{_SPACE * 3}WAIT_MIN: {tgen._wait_min}\n")
            file.write(f"{_SPACE * 3}WAIT_MAX: {tgen._wait_max}\n")
            file.write(f"{_SPACE * 3}GZIP: {str(tgen._gzip).lower()}\n")

        # write http servers

        http_servers = []
        if _ServiceType.http.name in _comps:
            http_servers = _comps[_ServiceType.http.name]

        for http_server in http_servers:
            assert(type(http_server) == HTTPServer)
            self.__write_service(file, http_server)

        # write dhcp servers

        dhcp_servers = []
        if _ServiceType.dhcp.name in _comps:
            dhcp_servers = _comps[_ServiceType.dhcp.name]

        for dhcp_server in dhcp_servers:
            assert(type(dhcp_server) == DHCPServer)
            self.__write_service(file, dhcp_server)

            file.write(f"{_SPACE * 3}# DHCP Server configuration:\n")
            file.write(f"{_SPACE * 3}LEASE_TIME: {dhcp_server._lease_time}\n")

            lease_starts = []
            lease_ends = []

            for config in dhcp_server._iface_configs:
                assert(type(config) == _IfaceConfig)

                assert(config._lease_start and config._lease_end)
                lease_starts.append(config._lease_start._str)
                lease_ends.append(config._lease_end._str)

            file.write(f"{_SPACE * 3}LEASE_STARTS: {" ".join(lease_starts)}\n")
            file.write(f"{_SPACE * 3}LEASE_ENDS: {" ".join(lease_ends)}\n")

        # write dns servers

        dns_servers = []
        if _ServiceType.dns.name in _comps:
            dns_servers = _comps[_ServiceType.dns.name]

        for dns_server in dns_servers:
            assert(type(dns_server) == DNSServer)
            self.__write_service(file, dns_server)

            file.write(f"{_SPACE * 3}# DNS Server configuration:\n")
            file.write(f"{_SPACE * 3}CACHE: {dns_server._cache}\n")
            file.write(f"{_SPACE * 3}LOG: {str(dns_server._log).lower()}\n")

            names = []
            ips = []

            for domain in dns_server._domains:
                assert(type(domain) == _Domain)

                names.append(domain._name)
                ips.append(domain._ip._str)

            file.write(f"{_SPACE * 3}HOST_NAMES: {" ".join(names)}\n")
            file.write(f"{_SPACE * 3}HOST_IPS: {" ".join(ips)}\n")

        # write load balancers

        router_id = 0  # necessary for ECMP advertisements

        lbs = []
        if _ServiceType.lb.name in _comps:
            lbs = _comps[_ServiceType.lb.name]

        for lb in lbs:
            assert(type(lb) == LoadBalancer)
            self.__write_service(file, lb)

            file.write(f"{_SPACE * 3}# Load Balancer configuration:\n")

            file.write(f"{_SPACE * 3}ROUTER_ID: {router_id}\n")
            router_id += 1

            file.write(f"{_SPACE * 3}TYPE: {lb._type.name}\n")
            file.write(f"{_SPACE * 3}ALGORITHM: {lb._algorithm.name}\n")
            file.write(f"{_SPACE * 3}ADVERTISE: {str(lb._advertise).lower()}\n")
            file.write(f"{_SPACE * 3}CHECK: {lb._health_check}\n")

            backends = []  # required
            for backend in lb._backends:
                assert(type(backend) == _IPv4)
                backends.append(backend._str)

            file.write(f"{_SPACE * 3}BACKENDS: {" ".join(backends)}\n")

        # write routers

        routers = []
        if _ServiceType.router.name in _comps:
            routers = _comps[_ServiceType.router.name]

        for router in routers:
            assert(type(router) == Router)
            self.__write_service(file, router)

            file.write(f"{_SPACE * 3}# Router configuration:\n")

            file.write(f"{_SPACE * 3}ROUTER_ID: {router_id}\n")
            router_id += 1

            file.write(f"{_SPACE * 3}ECMP: {router._ecmp.name}\n")

            cidrs = []
            nats = []
            costs = []

            for config in router._iface_configs:
                assert(type(config) == _IfaceConfig)

                cidrs.append(config._iface._cidr._str)
                nats.append(config._nat.name)
                costs.append(f"{config._cost}")

            file.write(f"{_SPACE * 3}CIDRS: {" ".join(cidrs)}\n")
            file.write(f"{_SPACE * 3}NATS: {" ".join(nats)}\n")
            file.write(f"{_SPACE * 3}COSTS: {" ".join(costs)}\n")

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
        file.write(f"{_SPACE * 5}cpus: {service._cpu_limit:.2f}\n")
        file.write(f"{_SPACE * 5}memory: {service._mem_limit}mb\n")

        # memory swap represents the total amount of memory and swap that can be used.
        file.write(f"{_SPACE * 2}memswap_limit: {service._swap_limit + service._mem_limit}mb\n")

        file.write(f"{_SPACE * 2}volumes:\n")
        file.write(f"{_SPACE * 3}- ./shared:/app/shared  # shared output\n")
        file.write(f"{_SPACE * 3}- /lib/modules:/lib/modules  # mount host kernel modules\n")

        if len(service._iface_configs):  # error if network map is empty
            file.write(f"{_SPACE * 2}networks:\n")

            for config in service._iface_configs:
                assert(type(config) == _IfaceConfig)
                file.write(f"{_SPACE * 3}- {config._iface._name}\n")

        file.write(f"{_SPACE * 2}cap_add:\n")
        file.write(f"{_SPACE * 3}- NET_ADMIN  # enables ifconfig, route\n")
        file.write(f"{_SPACE * 2}privileged: true  # enables sysctl, kernel modules\n")
        file.write(f"{_SPACE * 2}environment:\n")
        file.write(f"{_SPACE * 3}# Host configurations:\n")

        dns_servers = []
        if service._dns_servers:
            for dns_server in service._dns_servers:
                assert(type(dns_server) == _IPv4)
                dns_servers.append(dns_server._str)
        else:
            dns_servers.append("none")

        file.write(f"{_SPACE * 3}NAMESERVERS: {" ".join(dns_servers)}  # alternative name for dns server\n")
        file.write(f"{_SPACE * 3}FORWARD: {str(service._forward).lower()}\n")
        file.write(f"{_SPACE * 3}SYN_COOKIE: {service._syn_cookie.name}\n")
        file.write(f"{_SPACE * 3}CONGESTION_CONTROL: {service._congestion_control.name}\n")
        file.write(f"{_SPACE * 3}FAST_RETRAN: {str(service._fast_retran).lower()}\n")
        file.write(f"{_SPACE * 3}SACK: {str(service._sack).lower()}\n")
        file.write(f"{_SPACE * 3}TIMESTAMP: {str(service._timestamp).lower()}\n")
        file.write(f"{_SPACE * 3}TTL: {service._ttl}\n")

        ifaces = []
        ips = []
        net_masks = []
        gateways = []
        mtus = []
        firewalls = []

        for config in service._iface_configs:
            assert(type(config) == _IfaceConfig)

            ifaces.append(config._iface._name)
            ips.append(config._ip._str if config._ip else "none")
            net_masks.append(config._iface._cidr._netmask._str)
            gateways.append(config._gateway._str if config._gateway else "none")
            mtus.append(f"{config._mtu}" if config._mtu else "none")
            firewalls.append(config._firewall.name)

        # if no interfaces have been added, all of these variables will be empty
        
        file.write(f"{_SPACE * 3}# Interface configurations:\n")
        file.write(f"{_SPACE * 3}IFACES: {" ".join(ifaces)}\n")
        file.write(f"{_SPACE * 3}IPS: {" ".join(ips)}\n")
        file.write(f"{_SPACE * 3}NET_MASKS: {" ".join(net_masks)}\n")
        file.write(f"{_SPACE * 3}GATEWAYS: {" ".join(gateways)}\n")
        file.write(f"{_SPACE * 3}MTUS: {" ".join(mtus)}\n")
        file.write(f"{_SPACE * 3}FIREWALLS: {" ".join(firewalls)}\n")

        self.__write_tc_rules(file, service)

    def __write_tc_rules(self, file: TextIOWrapper, service: _Service):
        tc_rules = []
        rates = []
        delays = []
        jitters = []
        drops = []
        corrupts = []
        duplicates = []
        queue_limits = []

        for config in service._iface_configs:
            assert(type(config) == _IfaceConfig)

            tc_rule = config._tc_rule

            tc_rules.append("none")  # defaults
            rates.append("none")
            delays.append("none")
            jitters.append("none")
            drops.append("none")
            corrupts.append("none")
            duplicates.append("none")
            queue_limits.append("none")

            if isinstance(tc_rule, TCRate):
                tc_rules[-1] = "rate"
                rates[-1] = f"{tc_rule._rate}"
                queue_limits[-1] = f"{tc_rule._queue_limit}"

            elif isinstance(tc_rule, TCDelay):
                tc_rules[-1] ="delay" 
                delays[-1] = f"{tc_rule._delay}"
                jitters[-1] = f"{tc_rule._jitter}"
                queue_limits[-1] = f"{tc_rule._queue_limit}"

            elif isinstance(tc_rule, TCDrop):
                tc_rules[-1] = "drop"
                drops[-1] = f"{tc_rule._drop}"
                queue_limits[-1] = f"{tc_rule._queue_limit}"

            elif isinstance(tc_rule, TCCorrupt):
                tc_rules[-1] = "corrupt"
                corrupts[-1] = f"{tc_rule._corrupt}"
                queue_limits[-1] = f"{tc_rule._queue_limit}"

            elif isinstance(tc_rule, TCDuplicate):
                tc_rules[-1] = "duplicate"
                duplicates[-1] = f"{tc_rule._duplicate}"
                queue_limits[-1] = f"{tc_rule._queue_limit}"
        
        file.write(f"{_SPACE * 3}# TC Rule configurations:\n")
        file.write(f"{_SPACE * 3}TC_RULES: {" ".join(tc_rules)}\n")
        file.write(f"{_SPACE * 3}RATES: {" ".join(rates)}\n")
        file.write(f"{_SPACE * 3}DELAYS: {" ".join(delays)}\n")
        file.write(f"{_SPACE * 3}JITTERS: {" ".join(jitters)}\n")
        file.write(f"{_SPACE * 3}DROPS: {" ".join(drops)}\n")
        file.write(f"{_SPACE * 3}CORRUPTS: {" ".join(corrupts)}\n")
        file.write(f"{_SPACE * 3}DUPLICATES: {" ".join(duplicates)}\n")
        file.write(f"{_SPACE * 3}QUEUE_LIMITS: {" ".join(queue_limits)}\n")

    def __write_inets(self, file: TextIOWrapper):
        """
        @params:
            - file: File to write to.
        """

        ifaces = []
        if "iface" in _comps:
            ifaces = _comps["iface"]
            file.write("networks:\n")

        for iface in ifaces:
            assert(type(iface) == Iface)

            file.write(f"{_SPACE * 1}{iface._name}:\n")
            file.write(f"{_SPACE * 2}name: {iface._name}\n")
            file.write(f"{_SPACE * 2}driver: bridge\n")
            file.write(f"{_SPACE * 2}internal: true\n")
            file.write(f"{_SPACE * 2}ipam:\n")
            file.write(f"{_SPACE * 3}config:  # this is a workaround for a docker limitation\n")
            file.write(f"{_SPACE * 4}- subnet: {self.__get_cidr()}  # temporary subnet\n")
            file.write(f"{_SPACE * 2}driver_opts:  # os defines a suffix\n")
            file.write(f"{_SPACE * 3}com.docker.network.container_iface_prefix: {iface._name}_\n")

    def __get_cidr(self) -> str:
        """
        @returns: An IPv4 address in CIDR notation.
        """

        if self.__ip >= self.__ip_max:
            print(f"error: Allocated subnet {self.__cidr._str} exceeded.")
            print("info: Consider changing settings for the Configurator.")
            
            print_stack()
            exit(1)

        ip = _IPv4(self.__ip)
        cidr = f"{ip._str}/{self.__prefix_len}"

        suffix_len = 32 - self.__prefix_len
        self.__ip += 2 ** suffix_len  # iterate

        return cidr
