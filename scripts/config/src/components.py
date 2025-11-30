
from enum import Enum, auto
from traceback import print_stack


# IPv4 ************************************************************************


class _IPv4():
    def __init__(self, ip: str | int):
        """
        @params:
            - ip: The IPv4 address.
        """

        if type(ip) == str:
            if not self._is_legal(ip):
                print(f"error: Illegal IPv4 address {ip}")
                print_stack()
                exit(1)
        
            self._str = ip
            self._int = self._str_to_int(ip)
        elif type(ip) == int:
            if ip < 0 or ip > 0xffffffff:
                print(f"error: Illegal IPv4 address {ip}")
                print_stack()
                exit(1)

            self._int = ip
            self._str = self._int_to_str(ip)
        else:  # unknown type
            print(f"error: Illegal IPv4 of type {type(ip)}")
            print_stack()
            exit(1)

    def _is_legal(self, ip: str) -> bool:
        """
        @params:
            - ip: The IPv4 address as a string.
        @return: Whether the IPv4 address is legal dot notation.
        """

        octets = ip.split(".")
        if len(octets) != 4:
            return False

        try:
            octets = [*map(int, octets)]
        except Exception:
            return False

        for octet in octets:
            if octet < 0 or octet > 255:
                return False

        return True

    def _str_to_int(self, ip: str) -> int:
        """
        @params:
            - ip: The IPv4 address as a string, ex. "169.254.0.0"
        @returns: The IPv4 as an integer, ex. 0x0a000001
        """

        octets = ip.split(".")
        octets = [*map(int, octets)]

        ip =   (octets[0] << 24) \
             + (octets[1] << 16) \
             + (octets[2] << 8) \
             +  octets[3]
        
        return ip
    
    def _int_to_str(self, ip: int) -> str:
        """
        @params:
            - ip: The IPv4 as an integer, ex. 0x0a000001
        @returns: The IPv4 address as a string, ex. "169.254.0.0"
        """

        octets = [(0xff000000 & ip) >> 24,
                  (0x00ff0000 & ip) >> 16,
                  (0x0000ff00 & ip) >> 8,
                   0x000000ff & ip]
        
        octets = [*map(str, octets)]
        return ".".join(octets)


# CIDR ************************************************************************


class _Visibility(Enum):
    public = auto()
    private = auto()


class _CIDR():
    def __init__(self, cidr: str):
        """
        @params:
            - cidr: The subnet in CIDR notation, ex. "169.254.0.0/16"
        Note:
            - Subnets that overlap public and private IP ranges are disallowed.
        """

        if not self._is_legal(cidr):
            print(f"error: Illegal CIDR {cidr}")
            print_stack()
            exit(1)

        self._str = cidr

        ip, prefix_len = cidr.split("/")
        self._ip = _IPv4(ip)
        self._prefix_len = int(prefix_len)

        self._netmask = self._netmask(self._prefix_len)
        self._visibility = self._visibility(self._ip, self._prefix_len)

    def _is_legal(self, cidr: str) -> bool:
        """
        @params:
            - cidr: The subnet in CIDR notation, ex. "169.254.0.0/16"
        @return: Whether the IPv4 address is legal CIDR notation.
        """

        try:
            ip, prefix_len = cidr.split("/")
            ip = _IPv4(ip)

            prefix_len = int(prefix_len)
            if not 0 <= prefix_len <= 32:
                return False
        
        except Exception:
            return False
        
        return True

    def _netmask(self, prefix_len: int) -> _IPv4:
        """
        @params:
            - prefix_len: The prefix length of the subnet.
        @return: The netmask as an _IPv4 object.
        """

        suffix_len = 32 - prefix_len
        netmask: int = 0xffffffff ^ (2 ** suffix_len - 1)
        return _IPv4(netmask)
    
    def _visibility(self, ip: _IPv4, prefix_len: int) -> _Visibility:
        """
        @params:
            - ip: The IPv4 object.
            - prefix_len: The prefix length.
        @returns: Whether the CIDR address is private or public.
        """
        
        ip_private = _IPv4("10.0.0.0")
        visibility = self._visibility_internal(ip, prefix_len, ip_private, 8)
        if visibility == _Visibility.private:
            return visibility

        ip_private = _IPv4("169.254.0.0")
        visibility = self._visibility_internal(ip, prefix_len, ip_private, 16)
        if visibility == _Visibility.private:
            return visibility

        ip_private = _IPv4("172.16.0.0")
        visibility = self._visibility_internal(ip, prefix_len, ip_private, 12)
        if visibility == _Visibility.private:
            return visibility
        
        ip_private = _IPv4("192.168.0.0")
        visibility = self._visibility_internal(ip, prefix_len, ip_private, 16)
        if visibility == _Visibility.private:
            return visibility

        return _Visibility.public
    
    def _visibility_internal(self, ip: _IPv4, prefix_len: int, ip_private: _IPv4,
                              prefix_len_private: int) -> _Visibility:
        """
        @params:
            - ip: The IPv4 object.
            - prefix_len: The prefix length.
            - ip_private: The private IPv4 address.
            - prefix_len_private: The private prefix length.
        @return: Whether the CIDR address is private or public.
        """

        prefix_len_min = min(prefix_len, prefix_len_private)
        netmask_min = self._netmask(prefix_len_min)

        if ip._int & netmask_min._int == ip_private._int & netmask_min._int:
            if prefix_len < prefix_len_private:
                cidr_public = f"{ip._str}/{prefix_len}"
                cidr_private = f"{ip_private._str}/{prefix_len_private}"
                print(f"error: Public subnet {cidr_public} overlaps private subnet {cidr_private}.")
                print_stack()

                exit(1)

            return _Visibility.private
        return _Visibility.public
    
    def contains(self, ip: str) -> bool:
        """
        @params:
            - ip: The IPv4 address.
        @return: Whether the IPv4 address is within the CIDR range.
        """

        _ip = _IPv4(ip)
        if self._visibility_internal(_ip, 32, self._ip, self._prefix_len) == _Visibility.private:
            return True
        return False


# TC RULE *********************************************************************


class TCRule():
    def __init__(self, rate: int = 0, drop: int = 0, corrupt: int = 0, duplicate: int = 0,
                 delay: int = 0, jitter: int = 0, queue_limit: int =  2500):
        """
        @params:
            - rate: Set link bandwidth. A rate of 0 is unlimited. In units of kilobits per second.
            - drop: Drop random traffic. In unit of percents.
            - corrupt: Corrupt random packets. In units of percents.
            - duplicate: Duplicate random packets. In units of percents.
            - delay: Set a delay on traffic. In units of milliseconds.
            - jitter: Variance on delay, ex. delay +/- jitter. In units of milliseconds.
            - queue_limit: Maximum number of packets in queue.
        Note:
            - jitter requires that a delay is configured. If jitter is large enough, 
              packets will be reordered.
        """

        assert(rate >= 0)
        self._rate = rate

        assert(0 <= drop <= 100)
        self._drop = drop

        assert(0 <= corrupt <= 100)
        self._corrupt = corrupt

        assert(0 <= duplicate <= 100)
        self._duplicate = duplicate

        assert(delay >= 0 and jitter >= 0 and \
               delay - jitter >= 0)
        self._delay = delay
        self._jitter = jitter

        assert(queue_limit > 0)
        self._queue_limit = queue_limit


# INTERFACE *******************************************************************


class FirewallType(Enum):
    """
    block_new_conn_input: For customer devices. Connections must be initiated.
        - endpoints: Blocks unknown connections on INPUT received from the interface. 
        - routers:   Blocks unknown connections on FORWARD sent to the interface. 
                     Use on the internal interface of the router.
    block_new_conn_input_strict: Extends block_new_conn_input.
        - endpoints: Blocks OUTPUT sent on the interface to TCP ports: 22, 80, 443, 
                     5000, 7000, 9050; and UDP ports: 53, 67, 123, 443.
        - routers:   Blocks FORWARD received from the interface to TCP ports: 22, 80,
                     443, 5000, 7000, 9050; and UDP ports: 53, 123, 443.
    block_new_conn_output: For datacenter devices. Connections cannot be initiated.
        - endpoints: Blocks unknown connections on OUTPUT sent on the interface. 
        - routers:   Blocks unknown connections on FORWARD received on the interface. 
                     Use on the internal interface of the router.
    block_new_conn_output_strict: Extends block_new_conn_output.
        - endpoints: Blocks INPUT received on the interface to TCP ports: 22, 80, 443, 
                     5000, 7000, 9050; and UDP ports: 53, 67, 123, 443.
        - routers:   Blocks FORWARD sent on the interface to TCP ports: 22, 80,
                     443, 5000, 7000, 9050; and UDP ports: 53, 123, 443.
    block_rsts_output:
        - endpoints: Block TCP RSTs on OUTPUT sent on the interface. Useful for scapy scripts.
        - routers:   Blocks TCP RSTs on FORWARD received from the interface.
                     Use on the internal interface of routers.
    block_l4:
        - endpoints and routers: Block TCP and UDP on INPUT and OUTPUT. 
                                 Use on the external interface of routers.
    """

    block_new_conn_input = auto()
    block_new_conn_input_strict = auto()
    block_new_conn_output = auto()
    block_new_conn_output_strict = auto()
    block_rsts_output = auto()
    block_l4 = auto()


class NatType(Enum):
    """
    snat_input:  SNATS packets sent from an IP within the CIDR range of the corresponding
                 interface, ex. for the internal router interface of a home network. 
    snat_output: SNATS packets output on the corresponding interface, ex. for the internal
                 router interface of a datacenter network. 
    """

    snat_input = auto()
    snat_output = auto()


class Iface():
    def __init__(self):  # add to components
        if "iface" not in _comps:
            _comps["iface"] = []
        
        count = len(_comps["iface"])
        _comps["iface"].append(self)

        self._name = f"network-{count}"


class _IfaceConfig():
    def __init__(self, iface: Iface, cidr: str | None, ip: str | None, gateway: str | None, 
                 mtu: int | None, tc_rule: TCRule | None, firewall: FirewallType | None, 
                 lease_time: int | None = None, lease_start: str | None = None, 
                 lease_end: str | None = None, nat: NatType | None = None, cost: int | None = None):
        """
        @params:
            - iface: The network interface.
            - cidr: The subnet in CIDR notation, ex. "169.254.0.0/16". Required for DHCP.
            - ip: The IPv4 address of the service. Required for DHCP.
            - gateway: The IPv4 address of the gateway.
            - mtu: Configure the MTU. An MTU of none disables TSO.
            - tc_rule: The configured TC rule.
            - firewall: The configured firewall.
            - lease_time: Configure the duration that IPs are leased for.
            - lease_start: The IPv4 address at the start of the lease block. Only implemented on DHCP.
            - lease_end: The IPv4 address at the end of the lease block. Only implemented on DHCP.
            - nat: Configure NAT. Requires cidr to be configured. Only implemented on routers.
            - cost: The cost of routing traffic by the interface. Only implemented on routers.
        """

        self._iface = iface

        self._cidr = None
        if cidr:
            self._cidr = _CIDR(cidr)

        self._ip = None
        if ip:
            assert(self._cidr.contains(ip)) if self._cidr else True
            self._ip = _IPv4(ip)

        self._gateway = None
        if gateway:
            assert(self._cidr.contains(gateway)) if self._cidr else True
            self._gateway = _IPv4(gateway)

        self._mtu = None
        if mtu:
            assert(100 <= mtu <= 65535)
            self._mtu = mtu

        self._tc_rule = None
        if tc_rule:
            self._tc_rule = tc_rule

        self._firewall = firewall

        self._lease_time = None
        if lease_time:
            assert(lease_time > 0)
            self._lease_time = lease_time

        self._lease_start = None
        if lease_start:
            assert(self._cidr.contains(lease_start)) if self._cidr else True
            self._lease_start = _IPv4(lease_start)

        self._lease_end = None
        if lease_end:
            assert(self._cidr.contains(lease_end)) if self._cidr else True
            self._lease_end = _IPv4(lease_end)

        if self._lease_start or self._lease_end:
            assert(self._lease_start and self._lease_end)
            assert(self._lease_start._int <= self._lease_end._int)

        assert(cidr) if nat else True
        self._nat = nat

        self._cost = None
        if cost:
            assert(0 < cost <= 65535)
            self._cost = cost

    def __eq__(self, other) -> bool:
        assert isinstance(other, _IfaceConfig)
        if self._iface._name != other._iface._name:
            return False
        return True


# SERVICE *********************************************************************


class _ServiceType(Enum):
    http = auto()
    tgen = auto()  # traffic generator
    lb = auto()    # load balancer
    router = auto()
    client = auto()
    dhcp = auto()
    dns = auto()  # nameserver
    tor = auto()


class CongestionControlType(Enum):
    """
    The congestion control options are limited by the host kernel.
    For details see: https://en.wikipedia.org/wiki/TCP_congestion_control
      - List available options: sysctl net.ipv4.tcp_allowed_congestion_control OR lsmod | grep tcp_
      - List relevant kernel modules: ls /lib/modules/$(uname -r)/kernel/net/ipv4/ | grep tcp_
      - Install (non-persistent) kernel modules:
          - Create dependencies: sudo depmod
          - Add module: sudo modprobe <MODULE>
    """
    
    # default
    cubic = auto()
    reno = auto()

    # modules
    bbr = auto()
    bic = auto()
    cdg = auto()
    dctcp = auto()
    diag = auto()
    highspeed = auto()
    htcp = auto()
    hybla = auto()
    illinois = auto()
    lp = auto()
    nv = auto()
    scalable = auto()
    vegas = auto()
    veno = auto()
    westwood = auto()
    yeah = auto()


class SynCookieType(Enum):
    disable = auto()
    enable = auto()
    force = auto()


class _Service():
    def __init__(self, type: _ServiceType, image: str, auto_restart: bool, 
                 dns_servers: list[str] | str | None, log_queries: bool, cpu_limit: float, 
                 mem_limit: int, swap_limit: int, forward: bool, syn_cookie: SynCookieType, 
                 congestion_control: CongestionControlType, fast_retran: bool, 
                 sack: bool, timestamp: bool, ttl: int):
        """
        @params:
            - type: The type of the service.
            - image: The name of the Docker image.
            - auto_restart: If disabled, allows manually editing the configurations. 
                            Useful for development.
            - dns_servers: The IPv4 addresses of the DNS servers.
            - log_queries: Enable or disable access logs. Implemented on DNS, HTTP, and LB.
            - cpu_limit: Limit service cpu time. In units of number of logical cores. 
                         Ex. 0.1 is 10% of a logical core.
            - mem_limit: Limit service memory. In units of megabytes.
            - swap_limit: Limit swap memory. Set to 0 to disable swap. In units of megabytes.
            - forward: Enable or disable packet forwarding.
            - syn_cookie: Configure SYN cookies.
            - congestion_control: Configure congestion control.
            - fast_retran: Enable or disable fast retransmission.
            - sack: Enable or disable selective acknowledgments.
            - timestamp: Enable or disable tcp timestamps.
            - ttl: Configure the default ttl for packets.
        """

        self._type = type

        assert(image != "")
        self._image = image

        self._auto_restart = auto_restart

        assert(cpu_limit > 0)
        self._cpu_limit = cpu_limit

        assert(mem_limit > 32)  # minimum
        self._mem_limit = mem_limit

        assert(swap_limit >= 0)
        self._swap_limit = swap_limit
        
        self._dns_servers = None
        if dns_servers:
            self._dns_servers: list[_IPv4] = []

            if isinstance(dns_servers, str):
                dns_servers = [dns_servers]

            assert(0 < len(dns_servers) <= 64)
            for dns_server in dns_servers:
                ip = _IPv4(dns_server)
                self._dns_servers.append(ip)

        self._log_queries = log_queries
        self._forward = forward
        self._syn_cookie = syn_cookie
        self._congestion_control = congestion_control
        self._fast_retran = fast_retran
        self._sack = sack
        self._timestamp = timestamp

        assert(0 < ttl <= 255)
        self._ttl = ttl

        # add to components
        name = type.name
        if name not in _comps:
            _comps[name] = []

        count = len(_comps[name])
        _comps[name].append(self)

        self._name = f"{name}-{count}"
        self._iface_configs: list[_IfaceConfig] = []

    def add_iface(self, iface: Iface, cidr: str | None = None, ip: str | None = None, 
                  gateway: str | None = None, mtu: int | None = 1500, tc_rule: TCRule | None = None, 
                  firewall: FirewallType | None = None):
        """
        @params:
            - iface: The network interface.
            - cidr: The subnet in CIDR notation, ex. "169.254.0.0/16".
            - ip: The IPv4 address of the service.
            - gateway: The IPv4 address of the gateway.
            - mtu: Configure the MTU. An MTU of none disables TSO.
            - tc_rule: The configured TC rule.
            - firewall: The configured firewall.
        Note:
            - If the IP is empty, then the service will attempt to use DHCP for the IP, 
              gateway, and nameservers.
        """

        config = _IfaceConfig(iface, cidr, ip, gateway, mtu, tc_rule, firewall)

        assert(config not in self._iface_configs)
        self._iface_configs.append(config)


_comps: dict[str, list[Iface | _Service]] = {}  # created components are registered here


# CLIENT **********************************************************************


class Client(_Service):
    def __init__(self, dns_server: str | None = None, cpu_limit: float = 0.5, mem_limit: int = 256, 
                 swap_limit: int = 64, congestion_control: CongestionControlType = CongestionControlType.cubic,
                 fast_retran: bool = True, sack: bool = True, ttl: int = 64):
        """
        @params:
            - dns_server: The IPv4 addresses of the DNS server.
            - cpu_limit: Limit service cpu time. In units of number of logical cores. 
                         Ex. 0.1 is 10% of a logical core.
            - mem_limit: Limit service memory. In units of megabytes.
            - swap_limit: Limit swap memory. Set to 0 to disable swap. In units of megabytes.
            - congestion_control: Configure congestion control.
            - fast_retran: Enable or disable fast retransmission.
            - sack: Enable or disable selective acknowledgments.
            - ttl: Configure the default ttl for packets.
        """

        super().__init__(_ServiceType.client, "client", True, dns_server, False, 
                         cpu_limit, mem_limit, swap_limit, False, SynCookieType.enable, 
                         congestion_control, fast_retran, sack, True, ttl)


# TRAFFIC GENERATOR ***********************************************************


class Protocol(Enum):
    http = auto()
    https = auto()


class TrafficGenerator(_Service):
    def __init__(self, target: str, proto: Protocol = Protocol.http, requests: list[str] = ["/"],
                 conn_max: int = 50, conn_rate: int = 5, conn_dur: int = 10, wait_min: float = 5, 
                 wait_max: float = 15, gzip: bool = False, dns_server: str | None = None, 
                 cpu_limit: float = 0.5, mem_limit: int = 256, swap_limit: int = 64,
                 congestion_control: CongestionControlType = CongestionControlType.cubic,
                 fast_retran: bool = True, sack: bool = True, ttl: int = 64):
        """
        @params:
            - target: The IP address, or the domain name, of the target server.
            - proto: The protocol used for the requests.
            - requests: The files to request. Must be prefaced with '/'.
            - conn_max: The maximum number of simultaneous connections.
            - conn_rate: The rate of establishing new connections.
            - conn_dur: The average number of requests before closing the connection.
            - wait_min: The minimum wait between requests.
            - wait_max: The maximum wait between requests.
            - gzip: Enable or disable gzip compression.
            - dns_server: The IPv4 addresses of the DNS server.
            - cpu_limit: Limit service cpu time. In units of number of logical cores. 
                         Ex. 0.1 is 10% of a logical core.
            - mem_limit: Limit service memory. In units of megabytes.
            - swap_limit: Limit swap memory. Set to 0 to disable swap. In units of megabytes.
            - congestion_control: Configure congestion control.
            - fast_retran: Enable or disable fast retransmission.
            - sack: Enable or disable selective acknowledgments.
            - ttl: Configure the default ttl for packets.
        Note:
            - The traffic generator waits for 60 seconds before starting.
              This delay allows time for routes to settle on any routers.
            - The traffic generator prioritizes creating new connections over successful requests.
        """

        super().__init__(_ServiceType.tgen, "locust", True, dns_server, False, 
                         cpu_limit, mem_limit, swap_limit, False, SynCookieType.enable, 
                         congestion_control, fast_retran, sack, True, ttl)
        
        assert(target != "")
        self._target = target

        self._proto = proto

        assert(len(requests) > 0 and "" not in requests)
        self._requests = requests

        assert(conn_max > 0)
        self._conn_max = conn_max

        assert(conn_rate > 0)
        self._conn_rate = conn_rate

        assert(conn_dur > 0)
        self._conn_dur = conn_dur

        assert(wait_min >= 0 and wait_min <= wait_max)
        self._wait_min = wait_min

        assert(wait_max >= 0)  # must be >= wait_min
        self._wait_max = wait_max

        self._gzip = gzip


# HTTP SERVER *****************************************************************


class HTTPServer(_Service):
    def __init__(self, log_queries: bool = True, cpu_limit: float = 0.5, mem_limit: int = 256, 
                 swap_limit: int = 64, syn_cookie: SynCookieType = SynCookieType.enable, 
                 congestion_control: CongestionControlType = CongestionControlType.cubic,
                 fast_retran: bool = True, sack: bool = True, ttl: int = 64):
        """
        @params:
            - log_queries: Enable or disable access logs. Implemented on DNS, HTTP, and LB.
            - cpu_limit: Limit service cpu time. In units of number of logical cores. 
                         Ex. 0.1 is 10% of a logical core.
            - mem_limit: Limit service memory. In units of megabytes.
            - swap_limit: Limit swap memory. Set to 0 to disable swap. In units of megabytes.
            - syn_cookie: Configure SYN cookies.
            - congestion_control: Configure congestion control.
            - fast_retran: Enable or disable fast retransmission.
            - sack: Enable or disable selective acknowledgments.
            - ttl: Configure the default ttl for packets.
        Note:
            - Both HTTP (80) and HTTPS (443) are enabled.
            - In the real world, HTTPS requires a certificate signed by a trusted
              Certificate Authority (CA).
            - Many encrypted protocols require clock synchronization, such as HTTPS 
              and Tor. Docker uses the host clock so explicit synchronization, such
              as by NTP, is unnecessary.
        """

        super().__init__(_ServiceType.http, "nginx", True, None, log_queries, cpu_limit, 
                         mem_limit, swap_limit, False, syn_cookie, congestion_control, 
                         fast_retran, sack, True, ttl)


# DHCP SERVER *****************************************************************


class DHCPServer(_Service):
    def __init__(self, dns_server: str | None = None, cpu_limit: float = 0.5, mem_limit: int = 256, 
                 swap_limit: int = 64):
        """
        @params:
            - dns_server: The IPv4 addresses of the DNS server. The nameserver will be advertised.
            - cpu_limit: Limit service cpu time. In units of number of logical cores. 
                         Ex. 0.1 is 10% of a logical core.
            - mem_limit: Limit service memory. In units of megabytes.
            - swap_limit: Limit swap memory. Set to 0 to disable swap. In units of megabytes.
        Note:
            - The DHCP server will configure the DNS server, IP, CIDR, gateway, and MTU.
        """

        super().__init__(_ServiceType.dhcp, "udhcpd", True, dns_server, False, 
                         cpu_limit, mem_limit, swap_limit, False, SynCookieType.enable, 
                         CongestionControlType.cubic, True, True, True, 64)
        
    def add_iface(self, iface: Iface, cidr: str, ip: str, lease_time: int = 600, 
                  lease_start: str | None = None, lease_end: str | None = None, 
                  gateway: str | None = None, mtu: int | None = 1500, tc_rule: TCRule | None = None, 
                  firewall: FirewallType | None = None):
        """
        @params:
            - iface: The network interface.
            - cidr: The subnet in CIDR notation, ex. "169.254.0.0/16". CIDR will be advertised. Required.
            - ip: The IPv4 address of the service. Required.
            - lease_time: Configure the duration that IPs are leased for.
            - lease_start: The IPv4 address at the start of the lease block.
            - lease_end: The IPv4 address at the end of the lease block.
            - gateway: The IPv4 address of the gateway. The gateway will be advertised.
            - mtu: Configure the MTU. An MTU of none disables TSO. The MTU will be advertised.
            - tc_rule: The configured TC rule.
            - firewall: The configured firewall.
        Note:
            - The default lease_start is .10; the default lease_end is .254
            - The DHCP server may only have one interface.
        """

        _cidr = _CIDR(cidr)

        if not lease_start:  # default lease_start
            assert(_cidr._prefix_len <= 28)
            lease_start = _IPv4(_cidr._ip._int + 10)
            lease_start = lease_start._str

        if not lease_end:  # default lease_end
            assert(_cidr._prefix_len <= 28)
            suffix_len = 32 - _cidr._prefix_len
            lease_end = _IPv4(_cidr._ip._int + 2 ** suffix_len - 2)
            lease_end = lease_end._str

        config = _IfaceConfig(iface, cidr, ip, gateway, mtu, tc_rule, firewall, 
                              lease_time = lease_time, lease_start = lease_start, 
                              lease_end = lease_end)

        assert(len(self._iface_configs) == 0)  # only one interface
        self._iface_configs.append(config)


# DNS SERVER ******************************************************************


class _Domain():
    def __init__(self, name: str, ip: str):
        """
        @params:
            - name: The domain name.
            - ip: The IPv4 address of the service.
        """

        assert(name and name != "")
        self._name = name

        self._ip = _IPv4(ip)
    

class DNSServer(_Service):
    def __init__(self, cache: int = 600, dns_servers: list[str] | str | None = None, 
                 log_queries: bool = True, cpu_limit: float = 0.5, mem_limit: int = 256, 
                 swap_limit: int = 64, ttl: int = 64):
        """
        @params:
            - cache: The cache duration for the resolved record in seconds.
            - dns_servers: The IPv4 addresses of the DNS servers.
            - log_queries: Enable or disable access logs. Implemented on DNS, HTTP, and LB.
            - cpu_limit: Limit service cpu time. In units of number of logical cores. 
                         Ex. 0.1 is 10% of a logical core.
            - mem_limit: Limit service memory. In units of megabytes.
            - swap_limit: Limit swap memory. Set to 0 to disable swap. In units of megabytes.
            - ttl: Configure the default ttl for packets.
        Note:
            - resolv.conf only uses the first Nameserver. Most services use resolv.conf
              and are therefore limited to a single nameserver. 
              dnsmasq, on the other hand, is configured to use many nameservers.
            - Only Nameservers cache DNS responses. If DNS caching is important, 
              use a local Nameserver.
        """

        super().__init__(_ServiceType.dns, "dnsmasq", True, dns_servers, log_queries, 
                         cpu_limit, mem_limit, swap_limit, False, SynCookieType.enable, 
                         CongestionControlType.cubic, True, True, True, ttl)
        
        assert(cache > 0)
        self._cache = cache
        
        self._domains: list[_Domain] = []

    def register(self, name: str, ip: str):
        """
        @params:
            - name: The domain name.
            - ip: The IPv4 address of the service.
        """

        domain = _Domain(name, ip)
        self._domains.append(domain)


# Load Balancer ***************************************************************


class LBType(Enum):
    l4 = auto()  # neither support DSR
    l5 = auto()


class LBAlgorithm(Enum):
    roundrobin = auto()
    random = auto()
    leastconn = auto()
    source = auto()  # hash of the source IP
                     # each LB will hash the IP to the same value


class LoadBalancer(_Service):
    def __init__(self, backends: list[str], type: LBType = LBType.l5, 
                 algorithm: LBAlgorithm = LBAlgorithm.leastconn, advertise: bool = False, 
                 health_check: str = "/", log_queries: bool = True, cpu_limit: float = 0.5, 
                 mem_limit: int = 256, swap_limit: int = 64, syn_cookie: SynCookieType = SynCookieType.enable, 
                 congestion_control: CongestionControlType = CongestionControlType.cubic,
                 fast_retran: bool = True, sack: bool = True, ttl: int = 64):
        """
        @params:
            - backends: The list of IPv4 addresses to balance between.
            - type: The type of the load balancer.
            - algorithm: The algorithm to use for backend selection.
            - advertise: If enabled, all interfaces will be advertised by OSPF.
            - health_check: The server page to request for health checks.
            - log_queries: Enable or disable access logs. Implemented on DNS, HTTP, and LB.
            - cpu_limit: Limit service cpu time. In units of number of logical cores. 
                         Ex. 0.1 is 10% of a logical core.
            - mem_limit: Limit service memory. In units of megabytes.
            - swap_limit: Limit swap memory. Set to 0 to disable swap. In units of megabytes.
            - syn_cookie: Configure SYN cookies.
            - congestion_control: Configure congestion control.
            - fast_retran: Enable or disable fast retransmission.
            - sack: Enable or disable selective acknowledgments.
            - ttl: Configure the default ttl for packets.
        """

        super().__init__(_ServiceType.lb, "haproxy", True, None, log_queries, 
                         cpu_limit, mem_limit, swap_limit, False, syn_cookie, 
                         congestion_control, fast_retran, sack, True, ttl)

        assert(len(backends) > 0)
        self._backends: list[_IPv4] = []
        for backend in backends:
            ip = _IPv4(backend)
            self._backends.append(ip)
        
        self._type = type
        self._algorithm = algorithm
        self._advertise = advertise

        assert(health_check != "")
        self._health_check = health_check

        self._router_id = _get_router_id()


# ROUTER **********************************************************************


class ECMPType(Enum):
    l3 = auto()  # (Source IP, Destination IP, IP Protocol)
    l4 = auto()  # (Source IP, Destination IP, Source Port, Destination Port, IP Protocol)


class Router(_Service):
    def __init__(self, ecmp: ECMPType | None = None, cpu_limit: float = 0.5, 
                 mem_limit: int = 256, swap_limit: int = 64):
        """
        @params:
            - ecmp: Configure ECMP.
            - cpu_limit: Limit service cpu time. In units of number of logical cores. 
                         Ex. 0.1 is 10% of a logical core.
            - mem_limit: Limit service memory. In units of megabytes.
            - swap_limit: Limit swap memory. Set to 0 to disable swap. In units of megabytes.
        Note:
            - Uses OSPF for routing. OSPF filters for (1) the longest prefix match, 
              and then selects (2) the route with the lowest cost.
            - ECMP requires that CONFIG_IP_ROUTE_MULTIPATH is enabled on the host machine.
              See: `grep CONFIG_IP_ROUTE_MULTIPATH /boot/config-$(uname -r)`
        """

        super().__init__(_ServiceType.router, "bird", True, None, False, cpu_limit, 
                         mem_limit, swap_limit, True, SynCookieType.enable, 
                         CongestionControlType.cubic, True, True, True, 64)
        
        self._ecmp = ecmp
        self._router_id = _get_router_id()

    def add_iface(self, iface: Iface, cidr: str | None = None, ip: str | None = None, 
                  mtu: int | None = None, nat: NatType | None = None, cost: int = 10,
                  tc_rule: TCRule | None = None, firewall: FirewallType | None = None):
        """
        @params:
            - iface: The network interface.
            - cidr: The subnet in CIDR notation, ex. "169.254.0.0/16".
            - ip: The IPv4 address of the service.
            - mtu: Configure the MTU. An MTU of none disables TSO.
            - nat: Configure NAT. Requires cidr to be configured.
            - cost: The cost of routing traffic by the interface.
            - tc_rule: The configured TC rule.
            - firewall: The configured firewall.
        Note:
            - If the IP is empty, then the service will attempt to use DHCP for the IP, 
              gateway, and nameserver.
        """

        config = _IfaceConfig(iface, cidr, ip, None, mtu, tc_rule, firewall, 
                              nat = nat, cost = cost)
        
        assert(config not in self._iface_configs)
        self._iface_configs.append(config)


_router_id = 0   # necessary for ECMP advertisements; 0 is illegal
def _get_router_id() -> int:
    global _router_id

    _router_id += 1
    return _router_id
