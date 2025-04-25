
from io import TextIOWrapper
from subprocess import getstatusoutput
from math import ceil

from src.components import _comps, _ServiceType, _Service, _IfaceConfig, _IPv4, _CIDR, _Domain
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

        self.__config_hz = self.__get_interrupt_freq()

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

        # write dhcp

        dhcps = []
        if _ServiceType.dhcp.name in _comps:
            dhcps = _comps[_ServiceType.dhcp.name]

        for dhcp in dhcps:
            assert(type(dhcp) == DHCP)
            self.__write_service(file, dhcp)

            file.write(f"{_SPACE * 3}# DHCP configuration:\n")
            file.write(f"{_SPACE * 3}LEASE_TIME: {dhcp._lease_time}\n")

            lease_starts = []
            lease_ends = []

            for config in dhcp._iface_configs:
                assert(type(config) == _IfaceConfig)

                lease_starts.append(config._lease_start._str)
                lease_ends.append(config._lease_end._str)

            file.write(f"{_SPACE * 3}LEASE_STARTS: {" ".join(lease_starts)}\n")
            file.write(f"{_SPACE * 3}LEASE_ENDS: {" ".join(lease_ends)}\n")

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

        # write routers

        routers = []
        if _ServiceType.router.name in _comps:
            routers = _comps[_ServiceType.router.name]

        for i, router in enumerate(routers):
            assert(type(router) == Router)
            self.__write_service(file, router)

            file.write(f"{_SPACE * 3}# Router configuration:\n")
            file.write(f"{_SPACE * 3}ID: {i}\n")
            file.write(f"{_SPACE * 3}ECMP: {str(router._ecmp).lower()}\n")

            cidrs = []
            visibilities = []
            nats = []
            costs = []

            for config in router._iface_configs:
                assert(type(config) == _IfaceConfig)

                cidrs.append(config._iface._cidr._str)
                visibilities.append(config._iface._cidr._visibility.name)
                nats.append(config._nat.name)
                costs.append(f"{config._cost}")

            file.write(f"{_SPACE * 3}CIDRS: {" ".join(cidrs)}\n")
            file.write(f"{_SPACE * 3}VISIBILITIES: {" ".join(visibilities)}\n")
            file.write(f"{_SPACE * 3}NATS: {" ".join(nats)}\n")
            file.write(f"{_SPACE * 3}COSTS: {" ".join(costs)}\n")

        # write nameservers

        nameservers = []
        if _ServiceType.dns.name in _comps:
            nameservers = _comps[_ServiceType.dns.name]

        for nameserver in nameservers:
            assert(type(nameserver) == Nameserver)
            self.__write_service(file, nameserver)

            file.write(f"{_SPACE * 3}# Nameserver configuration:\n")
            file.write(f"{_SPACE * 3}TTL: {nameserver._ttl}\n")
            file.write(f"{_SPACE * 3}LOG: {str(nameserver._log).lower()}\n")

            names = []
            ips = []

            for domain in nameserver._domains:
                assert(type(domain) == _Domain)

                names.append(domain._name)
                ips.append(domain._ip._str)

            file.write(f"{_SPACE * 3}HOSTS: {" ".join(names)}\n")
            file.write(f"{_SPACE * 3}HOST_IPS: {" ".join(ips)}\n")

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
        file.write(f"{_SPACE * 3}- ./shared:/app/shared\n")
        file.write(f"{_SPACE * 3}- /lib/modules:/lib/modules  # mount host kernel modules\n")
        file.write(f"{_SPACE * 2}networks:\n")

        for config in service._iface_configs:
            assert(type(config) == _IfaceConfig)
            file.write(f"{_SPACE * 3}- {config._iface._name}\n")

        file.write(f"{_SPACE * 2}cap_add:\n")
        file.write(f"{_SPACE * 3}- NET_ADMIN  # enables ifconfig, route\n")
        file.write(f"{_SPACE * 2}privileged: true  # enables sysctl, kernel modules\n")
        file.write(f"{_SPACE * 2}environment:\n")
        file.write(f"{_SPACE * 3}# Host configurations:\n")

        nameservers = []

        if len(service._nameservers) == 0:
            nameservers.append("none")

        for nameserver in service._nameservers:
            assert(type(nameserver) == _IPv4)
            nameservers.append(nameserver._str)

        file.write(f"{_SPACE * 3}NAMESERVERS: {" ".join(nameservers)}\n")

        file.write(f"{_SPACE * 3}FORWARD: {str(service._forward).lower()}\n")
        file.write(f"{_SPACE * 3}SYN_COOKIE: {service._syn_cookie.name}\n")
        file.write(f"{_SPACE * 3}CONGESTION_CONTROL: {service._congestion_control.name}\n")
        file.write(f"{_SPACE * 3}FAST_RETRANS: {str(service._fast_retrans).lower()}\n")
        file.write(f"{_SPACE * 3}SACKS: {str(service._sacks).lower()}\n")
        file.write(f"{_SPACE * 3}TIMESTAMPS: {str(service._timestamps).lower()}\n")

        ifaces = []
        ips = []
        net_masks = []
        gateways = []
        rates = []
        firewalls = []
        drops = []
        delays = []
        mtus = []
        queue_times = []
        bursts = []

        for config in service._iface_configs:
            assert(type(config) == _IfaceConfig)

            ifaces.append(config._iface._name)
            ips.append(config._ip._str)
            net_masks.append(config._iface._cidr._netmask._str)
            gateways.append(config._gateway._str)
            rates.append(f"{config._rate:.3f}")
            firewalls.append(config._firewall.name)
            drops.append(f"{config._drop}")
            delays.append(f"{config._delay}")
            mtus.append(f"{config._mtu}")
            queue_times.append(f"{config._queue_time}")
            bursts.append(f"{self.__get_iface_burst(config)}")

        file.write(f"{_SPACE * 3}# Interface configurations:\n")
        file.write(f"{_SPACE * 3}IFACES: {" ".join(ifaces)}\n")
        file.write(f"{_SPACE * 3}IPS: {" ".join(ips)}\n")
        file.write(f"{_SPACE * 3}NET_MASKS: {" ".join(net_masks)}\n")
        file.write(f"{_SPACE * 3}GATEWAYS: {" ".join(gateways)}\n")
        file.write(f"{_SPACE * 3}RATES: {" ".join(rates)}  # mbits/s\n")
        file.write(f"{_SPACE * 3}FIREWALLS: {" ".join(firewalls)}\n")
        file.write(f"{_SPACE * 3}DROPS: {" ".join(drops)}  # %\n")
        file.write(f"{_SPACE * 3}DELAYS: {" ".join(delays)}  # ms\n")
        file.write(f"{_SPACE * 3}MTUS: {" ".join(mtus)}  # bytes\n")
        file.write(f"{_SPACE * 3}QUEUE_TIMES: {" ".join(queue_times)}  # ms\n")
        file.write(f"{_SPACE * 3}BURSTS: {" ".join(bursts)}  # kbits/s\n")

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
            print("\tConsider changing settings for the Configurator.")
            exit(1)

        ip = _IPv4(self.__ip)
        cidr = f"{ip._str}/{self.__prefix_len}"

        suffix_len = 32 - self.__prefix_len
        self.__ip += 2 ** suffix_len  # iterate

        return cidr

    def __get_interrupt_freq(self) -> int:
        """
        CONFIG_HZ represents the Kernel's interrupt frequency.
        Most Linux distributions include CONFIG_HZ within the /boot/config-$(uname -r) file.
        @returns: The CONFIG_HZ.
        """

        config_hz = 0

        s, o = getstatusoutput("grep 'CONFIG_HZ=' /boot/config-$(uname -r)")
        if s != 0:
            print("warning: Interrupt frequency not found. Link rate may be inaccurate.")
            config_hz = 250  # https://github.com/torvalds/linux/blob/master/kernel/Kconfig.hz

        else:
            try:
                config_hz = o.split("=")[1]
                config_hz = int(config_hz)
            except Exception as e:
                print(f"error: Unexpected output {o} for CONFIG_HZ.")
                print(f"\t{e}")
                exit(1)
        
        return config_hz

    def __get_iface_burst(self, config: _IfaceConfig) -> float:
        """
        The maximum amount of data that can be sent within a jiffy. This amount 
        may temporarily exceed the defined rate. At a minimum, burst should be
        large enough to support the rate.
        @params:
            - config: The _IfaceConfig to calculate the burst for.
        @returns: The burst in units of kilobits.
        Note:
            - This variable is being hidden to avoid dependencies between rate and burst.
        """

        burst = config._rate / self.__config_hz
        burst *= 1000          # convert mbits to kbits

        mtu = config._mtu * 8  # convert bytes to bits
        mtu /= 1000            # convert bits to kbits

        # the network will fail if the burst is too low
        if burst < mtu:
            burst = mtu
        
        burst = ceil(burst)
        return burst
