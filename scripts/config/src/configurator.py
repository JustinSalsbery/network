
from io import TextIOWrapper
from traceback import print_stack

from src.components import *  # private must be imported manually
from src.components import _components, _ServiceType, _Service, _IfaceConfig, _IPv4, _CIDR, _Domain
from src.grapher import Grapher


_SPACE = "  "

class Configurator():
    def __init__(
            self,
            available_range: str = "10.0.0.0/8",
            prefix_len: int = 22,
            color: bool = True,
            extra: bool = False,
        ):

        """
        @params:
            - available_range: The available IP range in CIDR notation for creating temporary subnets.
            - prefix_len: The size of each temporary subnet.
            - color: Enables or disables color in the graph.
            - extra: Enables or disables extra information in the graph.
        Note:
            - Outputs the configuration as `docker-compose.yml`.
            - The configurator MUST be called for the configuration to be created.
            - By default, Docker only supports around 30 network interfaces.
              By writing temporary subnets in the Docker Compose file we can exceed this limitation.
              The containers do not use these temporary subnets.
            - Docker will create a gateway at the .1 of each subnet; ex. 10.0.0.1 and 10.0.4.1.
              These gateways are internally and externally accessible and may interfere with 
              both container networking and host networking.
            - The available range MUST NOT overlap with any IPs in the configuration.
        """
        
        # create a temporary subnet

        self._cidr = _CIDR(available_range)
        self._ip = self._cidr._ip._int

        suffix_len = 32 - self._cidr._prefix_len
        self._ip_max = self._ip + 2 ** suffix_len

        self._prefix_len = prefix_len

        # docker compose down will fail unless networks follow after services
        with open("docker-compose.yml", "w") as file:
            self._write_services(file)
            self._write_inets(file)

        Grapher(color, extra)

    def _write_services(self, file: TextIOWrapper):
        """
        @params:
            - file: File to write to.
        """

        file.write("services:\n")

        # write clients

        clients = []
        if _ServiceType.client.name in _components:
            clients = _components[_ServiceType.client.name]

        for client in clients:
            assert isinstance(client, Client)
            self._write_service(file, client)

            tor_dir = client._tor_dir._name \
                if client._tor_dir \
                else ""

            tor_bridge = client._tor_bridge._name \
                if client._tor_bridge \
                else ""

            tor_middles = []
            if client._tor_middles:
                for tor_middle in client._tor_middles:
                    assert isinstance(tor_middle, TorNode)
                    tor_middles.append(tor_middle._name)

            tor_exits = []
            if client._tor_exits:
                for tor_exit in client._tor_exits:
                    assert isinstance(tor_exit, TorNode)
                    tor_exits.append(tor_exit._name)

            file.write(f"{_SPACE * 3}# Tor configuration:\n")
            file.write(f"{_SPACE * 3}TOR_DIR: {tor_dir}\n")
            file.write(f"{_SPACE * 3}TOR_BRIDGE: {tor_bridge}\n")
            file.write(f"{_SPACE * 3}TOR_MIDDLES: {" ".join(tor_middles)}\n")
            file.write(f"{_SPACE * 3}TOR_EXITS: {" ".join(tor_exits)}\n")
            file.write(f"{_SPACE * 3}TOR_LOG: {str(client._tor_log).lower()}\n")

        # write traffic generators

        tgens = []
        if _ServiceType.tgen.name in _components:
            tgens = _components[_ServiceType.tgen.name]

        for tgen in tgens:
            assert isinstance(tgen, TrafficGenerator)
            self._write_service(file, tgen)

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
        if _ServiceType.http.name in _components:
            http_servers = _components[_ServiceType.http.name]

        for http_server in http_servers:
            assert isinstance(http_server, HTTPServer)
            self._write_service(file, http_server)

            tor_dir = http_server._tor_dir._name \
                if http_server._tor_dir \
                else ""

            tor_bridge = http_server._tor_bridge._name \
                if http_server._tor_bridge \
                else ""

            tor_middles = []
            if http_server._tor_middles:
                for tor_middle in http_server._tor_middles:
                    assert isinstance(tor_middle, TorNode)
                    tor_middles.append(tor_middle._name)

            tor_exits = []
            if http_server._tor_exits:
                for tor_exit in http_server._tor_exits:
                    assert isinstance(tor_exit, TorNode)
                    tor_exits.append(tor_exit._name)

            file.write(f"{_SPACE * 3}# Tor configuration:\n")
            file.write(f"{_SPACE * 3}TOR_DIR: {tor_dir}\n")
            file.write(f"{_SPACE * 3}TOR_BRIDGE: {tor_bridge}\n")
            file.write(f"{_SPACE * 3}TOR_MIDDLES: {" ".join(tor_middles)}\n")
            file.write(f"{_SPACE * 3}TOR_EXITS: {" ".join(tor_exits)}\n")
            file.write(f"{_SPACE * 3}TOR_LOG: {str(http_server._tor_log).lower()}\n")

        # write dhcp servers

        dhcp_servers = []
        if _ServiceType.dhcp.name in _components:
            dhcp_servers = _components[_ServiceType.dhcp.name]

        for dhcp_server in dhcp_servers:
            assert isinstance(dhcp_server, DHCPServer)
            self._write_service(file, dhcp_server)

            lease_times = []
            lease_starts = []
            lease_ends = []

            for config in dhcp_server._iface_configs:
                assert isinstance(config, _IfaceConfig)
                
                lease_times.append(f"{config._lease_time}")
                lease_starts.append(config._lease_start._str)
                lease_ends.append(config._lease_end._str)

            file.write(f"{_SPACE * 3}# DHCP Server configuration:\n")
            file.write(f"{_SPACE * 3}LEASE_TIMES: {" ".join(lease_times)}\n")
            file.write(f"{_SPACE * 3}LEASE_STARTS: {" ".join(lease_starts)}\n")
            file.write(f"{_SPACE * 3}LEASE_ENDS: {" ".join(lease_ends)}\n")

        # write dns servers

        dns_servers = []
        if _ServiceType.dns.name in _components:
            dns_servers = _components[_ServiceType.dns.name]

        for dns_server in dns_servers:
            assert isinstance(dns_server, DNSServer)
            self._write_service(file, dns_server)

            names = []
            ips = []

            for domain in dns_server._domains:
                assert isinstance(domain, _Domain)

                names.append(domain._name)
                ips.append(domain._ip._str)

            file.write(f"{_SPACE * 3}# DNS Server configuration:\n")
            file.write(f"{_SPACE * 3}CACHE: {dns_server._cache}\n")
            file.write(f"{_SPACE * 3}HOST_NAMES: {" ".join(names)}\n")
            file.write(f"{_SPACE * 3}HOST_IPS: {" ".join(ips)}\n")

        # write load balancers

        lbs = []
        if _ServiceType.lb.name in _components:
            lbs = _components[_ServiceType.lb.name]

        for lb in lbs:
            assert isinstance(lb, LoadBalancer)
            self._write_service(file, lb)

            backends = []

            for backend in lb._backends:
                assert isinstance(backend, _IPv4)
                backends.append(backend._str)

            file.write(f"{_SPACE * 3}# Load Balancer configuration:\n")
            file.write(f"{_SPACE * 3}ROUTER_ID: {lb._router_id}\n")
            file.write(f"{_SPACE * 3}TYPE: {lb._type.name}\n")
            file.write(f"{_SPACE * 3}ALGORITHM: {lb._algorithm.name}\n")
            file.write(f"{_SPACE * 3}ADVERTISE: {str(lb._advertise).lower()}\n")
            file.write(f"{_SPACE * 3}CHECK: {lb._health_check}\n")
            file.write(f"{_SPACE * 3}BACKENDS: {" ".join(backends)}\n")

        # write tor nodes

        tor_nodes = []
        if _ServiceType.tor.name in _components:
            tor_nodes = _components[_ServiceType.tor.name]

        for tor_node in tor_nodes:
            assert isinstance(tor_node, TorNode)
            self._write_service(file, tor_node)

            tor_dir = tor_node._tor_dir._name \
                if tor_node._tor_dir \
                else tor_node._name

            file.write(f"{_SPACE * 3}# Tor configuration:\n")
            file.write(f"{_SPACE * 3}TOR_DIR: {tor_dir}\n")
            file.write(f"{_SPACE * 3}TOR_LOG: {str(tor_node._tor_log).lower()}\n")
            file.write(f"{_SPACE * 3}IS_BRIDGE: {str(tor_node._is_bridge).lower()}\n")
            file.write(f"{_SPACE * 3}IS_EXIT: {str(tor_node._is_exit).lower()}\n")

        # write routers

        routers = []
        if _ServiceType.router.name in _components:
            routers = _components[_ServiceType.router.name]

        for router in routers:
            assert isinstance(router, Router)
            self._write_service(file, router)

            ecmp = router._ecmp.name if router._ecmp else "none"

            cidrs = []
            nats = []
            costs = []

            for config in router._iface_configs:
                assert isinstance(config, _IfaceConfig)

                cidrs.append(config._cidr._str if config._cidr else "none")
                nats.append(config._nat.name if config._nat else "none")
                costs.append(f"{config._cost}")

            file.write(f"{_SPACE * 3}# Router configuration:\n")
            file.write(f"{_SPACE * 3}ROUTER_ID: {router._router_id}\n")
            file.write(f"{_SPACE * 3}ECMP: {ecmp}\n")
            file.write(f"{_SPACE * 3}CIDRS: {" ".join(cidrs)}\n")
            file.write(f"{_SPACE * 3}NATS: {" ".join(nats)}\n")
            file.write(f"{_SPACE * 3}COSTS: {" ".join(costs)}\n")

    def _write_service(self, file: TextIOWrapper, service: _Service):
        """
        @params:
            - file: File to write to.
            - service: Service configuration to write.
        """

        # write component

        file.write(f"{_SPACE * 1}{service._name}:\n")
        file.write(f"{_SPACE * 2}image: {service._image}\n")
        file.write(f"{_SPACE * 2}container_name: {service._name}\n")
        file.write(f"{_SPACE * 2}hostname: {service._name}\n")
        file.write(f"{_SPACE * 2}restart: unless-stopped\n")

        # write limits

        file.write(f"{_SPACE * 2}deploy:\n")
        file.write(f"{_SPACE * 3}resources:\n")
        file.write(f"{_SPACE * 4}limits:\n")
        file.write(f"{_SPACE * 5}cpus: {service._cpu_limit:.2f}\n")
        file.write(f"{_SPACE * 5}memory: {service._mem_limit}mb\n")

        # memory swap represents the total amount of memory and swap that can be used.
        file.write(f"{_SPACE * 2}memswap_limit: {service._swap_limit + service._mem_limit}mb\n")

        # write logging

        file.write(f"{_SPACE * 2}logging:  # limit log size\n")
        file.write(f"{_SPACE * 3}driver: json-file\n")
        file.write(f"{_SPACE * 3}options:\n")
        file.write(f"{_SPACE * 4}max-size: 16mb\n")

        # write volumes

        file.write(f"{_SPACE * 2}volumes:\n")
        file.write(f"{_SPACE * 3}- ./shared:/app/shared  # shared output\n")
        file.write(f"{_SPACE * 3}- /lib/modules:/lib/modules  # mount host kernel modules\n")

        # write networks

        if len(service._iface_configs):  # avoids an error if the network map is empty
            file.write(f"{_SPACE * 2}networks:\n")

            for config in service._iface_configs:
                assert isinstance(config, _IfaceConfig)
                file.write(f"{_SPACE * 3}- {config._iface._name}\n")

        # write permissions

        file.write(f"{_SPACE * 2}cap_add:\n")
        file.write(f"{_SPACE * 3}- NET_ADMIN  # enables ifconfig, route\n")
        file.write(f"{_SPACE * 2}privileged: true  # enables sysctl, kernel modules\n")

        file.write(f"{_SPACE * 2}environment:\n")

        # write host configurations

        dns_servers = []
        if not service._dns_servers:
            dns_servers.append("none")
        else:
            for dns_server in service._dns_servers:
                assert isinstance(dns_server, _IPv4)
                dns_servers.append(dns_server._str)

        file.write(f"{_SPACE * 3}# Host configuration:\n")
        file.write(f"{_SPACE * 3}NAMESERVERS: {" ".join(dns_servers)}\n")
        file.write(f"{_SPACE * 3}LOG_QUERIES: {str(service._log_queries).lower()}\n")
        file.write(f"{_SPACE * 3}FORWARD: {str(service._forward).lower()}\n")
        file.write(f"{_SPACE * 3}SYN_COOKIE: {service._syn_cookie.name}\n")
        file.write(f"{_SPACE * 3}CONGESTION_CONTROL: {service._congestion_control.name}\n")
        file.write(f"{_SPACE * 3}FAST_RETRAN: {str(service._fast_retran).lower()}\n")
        file.write(f"{_SPACE * 3}SACK: {str(service._sack).lower()}\n")
        file.write(f"{_SPACE * 3}TIMESTAMP: {str(service._timestamp).lower()}\n")
        file.write(f"{_SPACE * 3}AUTO_RESTART: {str(service._auto_restart).lower()}\n")
        file.write(f"{_SPACE * 3}TTL: {service._ttl}\n")

        # write interface configurations

        ifaces = []
        ips = []
        net_masks = []
        gateways = []
        mtus = []
        firewalls = []

        for config in service._iface_configs:
            assert isinstance(config, _IfaceConfig)

            ifaces.append(config._iface._name)
            ips.append(config._ip._str if config._ip else "none")
            net_masks.append(config._cidr._netmask._str if config._cidr else "none")
            gateways.append(config._gateway._str if config._gateway else "none")
            mtus.append(f"{config._mtu}" if config._mtu else "none")
            firewalls.append(config._firewall.name if config._firewall else "none")

        # if no interfaces have been added, all of these variables will be empty
        file.write(f"{_SPACE * 3}# Interface configurations:\n")
        file.write(f"{_SPACE * 3}IFACES: {" ".join(ifaces)}\n")
        file.write(f"{_SPACE * 3}IPS: {" ".join(ips)}\n")
        file.write(f"{_SPACE * 3}NET_MASKS: {" ".join(net_masks)}\n")
        file.write(f"{_SPACE * 3}GATEWAYS: {" ".join(gateways)}\n")
        file.write(f"{_SPACE * 3}MTUS: {" ".join(mtus)}\n")
        file.write(f"{_SPACE * 3}FIREWALLS: {" ".join(firewalls)}\n")

        # write tc_rules

        rates = []
        delays = []
        jitters = []
        drops = []
        corrupts = []
        duplicates = []
        queue_limits = []

        for config in service._iface_configs:
            assert isinstance(config, _IfaceConfig)

            tc_rule = config._tc_rule
            rates.append(f"{tc_rule._rate}" if tc_rule else "none")
            delays.append(f"{tc_rule._delay}" if tc_rule else "none")
            jitters.append(f"{tc_rule._jitter}" if tc_rule else "none")
            drops.append(f"{tc_rule._drop}" if tc_rule else "none")
            corrupts.append(f"{tc_rule._corrupt}" if tc_rule else "none")
            duplicates.append(f"{tc_rule._duplicate}" if tc_rule else "none")
            queue_limits.append(f"{tc_rule._queue_limit}" if tc_rule else "none")
        
        file.write(f"{_SPACE * 3}# TC Rule configurations:\n")
        file.write(f"{_SPACE * 3}RATES: {" ".join(rates)}\n")
        file.write(f"{_SPACE * 3}DELAYS: {" ".join(delays)}\n")
        file.write(f"{_SPACE * 3}JITTERS: {" ".join(jitters)}\n")
        file.write(f"{_SPACE * 3}DROPS: {" ".join(drops)}\n")
        file.write(f"{_SPACE * 3}CORRUPTS: {" ".join(corrupts)}\n")
        file.write(f"{_SPACE * 3}DUPLICATES: {" ".join(duplicates)}\n")
        file.write(f"{_SPACE * 3}QUEUE_LIMITS: {" ".join(queue_limits)}\n")

    def _write_inets(self, file: TextIOWrapper):
        """
        @params:
            - file: File to write to.
        """

        ifaces = []
        if "iface" in _components:
            ifaces = _components["iface"]
            file.write("networks:\n")

        for iface in ifaces:
            assert isinstance(iface, Iface)

            file.write(f"{_SPACE * 1}{iface._name}:\n")
            file.write(f"{_SPACE * 2}name: {iface._name}\n")
            file.write(f"{_SPACE * 2}driver: bridge\n")
            file.write(f"{_SPACE * 2}internal: true\n")
            file.write(f"{_SPACE * 2}ipam:\n")
            file.write(f"{_SPACE * 3}config:  # this is a workaround for a docker limitation\n")
            file.write(f"{_SPACE * 4}- subnet: {self._get_cidr()}  # temporary subnet\n")
            file.write(f"{_SPACE * 2}driver_opts:  # os defines a suffix\n")
            file.write(f"{_SPACE * 3}com.docker.network.container_iface_prefix: {iface._name}_\n")

    def _get_cidr(self) -> str:
        """
        @returns: An IPv4 address in CIDR notation.
        """

        if self._ip >= self._ip_max:
            print(f"error: Allocated subnet {self._cidr._str} exceeded.")
            print("info: Consider changing settings for the Configurator.")
            
            print_stack()
            exit(1)

        ip = _IPv4(self._ip)
        cidr = f"{ip._str}/{self._prefix_len}"

        suffix_len = 32 - self._prefix_len
        self._ip += 2 ** suffix_len  # iterate

        return cidr
