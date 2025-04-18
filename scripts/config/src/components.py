
from enum import Enum, auto
from random import choice
from math import nan


_comps = {} # Created components are registered here.


# IPv4 ************************************************************************


class _Visibility(Enum):
    public = auto()
    private = auto()


class _IPv4():
    def __init__(self, ip: str | int):
        """
        @params:
            - ip: The IPv4 address.
        """

        if ip == "":  # special case
            self._str = "none"
            self._int = nan
            return

        if type(ip) == str:
            if not self.__is_legal(ip):
                print(f"error: Illegal IPv4 address {ip}")
                exit(1)
        
            self._str = ip
            self._int = self.__str_to_int(ip)
        elif type(ip) == int:
            if ip < 0 or ip > 0xffffffff:
                print(f"error: Illegal IPv4 address {ip}")
                exit(1)

            self._int = ip
            self._str = self.__int_to_str(ip)
        else:  # unknown type
            print(f"error: Illegal IPv4 of type {type(ip)}")
            exit(1)

    def __is_legal(self, ip: str) -> bool:
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

    def __str_to_int(self, ip: str) -> int:
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
    
    def __int_to_str(self, ip: int) -> str:
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
    
    def __str__(self) -> str:
        return f"{"{"} {self._str} {"}"}"


class _CIDR():
    def __init__(self, cidr: str):
        """
        @params:
            - cidr: The subnet in CIDR notation, ex. "169.254.0.0/16"
        WARNING:
            - Subnets that overlap public and private IP ranges are disallowed.
            - The maximum allowed prefix length is 28.
        """

        if not self.__is_legal(cidr):
            print(f"error: Illegal CIDR {cidr}")
            exit(1)

        self._str = cidr

        ip, prefix_len = cidr.split("/")
        self._ip = _IPv4(ip)
        self._prefix_len = int(prefix_len)

        self._netmask = self.__netmask(self._prefix_len)
        self._visibility = self.__visibility(cidr, self._ip, self._prefix_len)

    def __is_legal(self, cidr: str) -> bool:
        """
        @params:
            - cidr: The subnet in CIDR notation, ex. "169.254.0.0/16"
        @return: Whether the IPv4 address is legal CIDR notation.
        """

        try:
            ip, prefix_len = cidr.split("/")

            ip = _IPv4(ip)
            if ip._str == "none":
                return False

            prefix_len = int(prefix_len)
            if not 0 <= prefix_len <= 28:
                return False
        
        except Exception:
            return False
        
        return True

    def __netmask(self, prefix_len: int) -> _IPv4:
        """
        @params:
            - prefix_len: The prefix length of the subnet.
        @return: The netmask as an _IPv4 object.
        """

        suffix_len = 32 - prefix_len
        netmask = 0xffffffff ^ (2 ** suffix_len - 1)
        return _IPv4(netmask)
    
    def __visibility(self, cidr: str, ip: _IPv4, prefix_len: int) -> _Visibility:
        """
        @params:
            - cidr: The subnet in CIDR notation, ex. "169.254.0.0/16"
            - ip: The IPv4 object.
            - prefix_len: The prefix length.
        @returns: Whether the CIDR address is private or public.
        """
        
        ip_private = _IPv4("10.0.0.0")
        visibility = self.__visibility_internal(cidr, ip, prefix_len, ip_private, 8)
        if visibility == _Visibility.private:
            return visibility

        ip_private = _IPv4("169.254.0.0")
        visibility = self.__visibility_internal(cidr, ip, prefix_len, ip_private, 16)
        if visibility == _Visibility.private:
            return visibility

        ip_private = _IPv4("172.16.0.0")
        visibility = self.__visibility_internal(cidr, ip, prefix_len, ip_private, 12)
        if visibility == _Visibility.private:
            return visibility
        
        ip_private = _IPv4("192.168.0.0")
        visibility = self.__visibility_internal(cidr, ip, prefix_len, ip_private, 16)
        if visibility == _Visibility.private:
            return visibility

        return _Visibility.public
    
    def __visibility_internal(self, cidr: str, ip: _IPv4, prefix_len: int, ip_private: _IPv4,
                              prefix_len_private: int) -> _Visibility:    
        """
        @params:
            - cidr: The subnet in CIDR notation, ex. "169.254.0.0/16"
            - ip: The IPv4 object.
            - prefix_len: The prefix length.
            - ip_private: The private IPv4 address.
            - prefix_len_private: The private prefix length.
        @return: Whether the CIDR address is private or public.
        """

        prefix_len_min = min(prefix_len, prefix_len_private)
        netmask_min = self.__netmask(prefix_len_min)

        if ip._int & netmask_min._int == ip_private._int & netmask_min._int:
            if prefix_len < prefix_len_private:
                cidr_private = f"{ip_private._str}/{prefix_len_private}"
                print(f"error: Public subnet {cidr} overlaps private subnet {cidr_private}.")
                exit(1)

            return _Visibility.private
        return _Visibility.public
    
    def __str__(self) -> str:
        return f"{"{"} {self._str}, {self._netmask}, {self._visibility.name} {"}"}"


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

    none = auto()
    block_new_conn_input = auto()
    block_new_conn_input_strict = auto()
    block_new_conn_output = auto()
    block_new_conn_output_strict = auto()
    block_rsts_output = auto()
    block_l4 = auto()


class NatType(Enum):
    """
    snat_input:  For the internal router interface of a customer network. SNATS packets sent
                 from an IP within the CIDR range of the corresponding interface.
    snat_output: For the internal router interface of a datacenter network. SNATS packets
                 output on the corresponding interface.
    """

    none = auto()
    snat_input = auto()
    snat_output = auto()


class Iface():
    def __init__(self, cidr: str):
        """
        @params:
            - cidr: The subnet in CIDR notation, ex. "169.254.0.0/16"
        """

        if "Iface" not in _comps:
            _comps["Iface"] = []
        
        count = len(_comps["Iface"])
        _comps["Iface"].append(self)

        self._name = f"network-{count}"
        self._cidr = _CIDR(cidr)
        
    def __str__(self) -> str:
        return f"{"{"} {self._name}, {self._cidr} {"}"}"


class _IfaceConfig():
    def __init__(self, iface: Iface, ip: str, gateway: str, firewall: FirewallType, 
                 drop_percent: int, delay: int, lease_start: str, lease_end: str, 
                 nat: NatType):
        """
        @params:
            - iface: The network interface.
            - ip: The IPv4 address of the service.
            - gateway: The IPv4 address of the gateway.
            - firewall: Configure firewall.
            - drop_percent: Drop a percent of random traffic. From 0 to 100.
            - delay: Set a delay on traffic. In units of milliseconds.
            - lease_start: The IPv4 address at the start of the lease block. Only implemented on DHCP.
            - lease_end: The IPv4 address at the end of the lease block. Only implemented on DHCP.
            - nat: Configure NAT. Only implemented on routers.
        """

        self._iface = iface
        self._ip = _IPv4(ip)
        self._gateway = _IPv4(gateway)
        self._firewall = firewall

        assert(0 <= drop_percent <= 100)
        self._drop_percent = drop_percent

        assert(0 <= delay)
        self._delay = delay

        self._lease_start = _IPv4(lease_start)
        self._lease_end = _IPv4(lease_end)
        self._nat = nat

    def __str__(self) -> str:
        return f"{"{"} {self._iface}, {self._src}, {self._gateway} {"}"}"


# SERVICE *********************************************************************


class _ServiceType(Enum):
    server = auto()
    tgen = auto()  # traffic generator
    lb = auto()  # load balancer
    router = auto()
    client = auto()
    dhcp = auto()
    dns = auto()  # nameserver


class CongestionControlType(Enum):
    cubic = auto()  # alpine default
    reno = auto()


class SynCookieType(Enum):
    disable = auto()
    enable = auto()
    force = auto()


class _Service():
    def __init__(self, type: _ServiceType, image: str, cpu_limit: str, mem_limit: str, 
                 disable_swap: bool, nameserver: str, forward: bool, syn_cookie: SynCookieType, 
                 congestion_control: CongestionControlType):
        """
        @params:
            - type: The type of the service.
            - image: The name of the Docker image.
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
            - nameserver: The IPv4 address.
            - forward: Enable or disable packet forwarding.
            - syn_cookie: Configure SYN cookies.
            - congestion_control: Configure congestion control.
        """

        self._type = type
        self._image = image
        self._cpu_limit = cpu_limit
        self._mem_limit = mem_limit
        self._disable_swap = disable_swap
        self._nameserver = _IPv4(nameserver)
        self._forward = forward
        self._syn_cookie = syn_cookie
        self._congestion_control = congestion_control

        name = type.name
        if name not in _comps:
            _comps[name] = []

        count = len(_comps[name])
        _comps[name].append(self)

        self._name = f"{name}-{count}"
        self._iface_configs = []

    def add_iface(self, iface: Iface, ip: str = "", gateway: str = "", firewall: FirewallType = FirewallType.none, 
                  drop_percent: int = 0, delay: int = 0) -> None:
        """
        @params:
            - iface: The network interface.
            - ip: The IPv4 address of the service.
            - gateway: The IPv4 address of the gateway.
            - firewall: Configure firewall.
            - drop_percent: Drop a percent of random traffic. From 0 to 100.
            - delay: Set a delay on traffic. In units of milliseconds.
        WARNING:
            - If the IP is empty, then the service will attempt to use DHCP
              for the IP, gateway, and nameserver.
        """

        config = _IfaceConfig(iface, ip, gateway, firewall, drop_percent, delay, "", "", NatType.none)
        self._iface_configs.append(config)

    def __str__(self):
        return f"{"{"} {self._name}, {self._image}, {self._iface_configs} {"}"}"


# TRAFFIC GENERATOR ***********************************************************


class Protocol(Enum):
    http = auto()
    https = auto()


class TrafficGenerator(_Service):
    def __init__(self, target: str, proto: Protocol = Protocol.http,
                 pages: list[str] = ["/"], conn_max: int = 500, conn_rate: int = 5, 
                 wait_min: float = 5, wait_max: float = 15, cpu_limit: str = "0.5", 
                 mem_limit: str = "256M", disable_swap: bool = False, nameserver: str = "",
                 forward: bool = False, syn_cookie: SynCookieType = SynCookieType.enable, 
                 congestion_control: CongestionControlType = CongestionControlType.cubic):
        """
        @params:
            - target: The IP address, or the domain, of the target server.
            - proto: The protocol used for the requests.
            - pages: The pages to request.
            - conn_max: The maximum number of simultaneous connections.
            - conn_rate: The rate of establishing new connections.
            - wait_min: The minimum wait between requests.
            - wait_max: The maximum wait between requests.
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - nameserver: The IPv4 address.
            - forward: Enable or disable packet forwarding.
            - syn_cookie: Configure SYN cookies.
            - congestion_control: Configure congestion control.
        """

        super().__init__(_ServiceType.tgen, "locust", cpu_limit, mem_limit, 
                         disable_swap, nameserver, forward, syn_cookie, congestion_control)
        
        self._target = target
        self._proto = proto.name
        self._pages = pages
        self._conn_max = conn_max
        self._conn_rate = conn_rate
        self._wait_min = wait_min
        self._wait_max = wait_max

    def __str__(self) -> str:
        return f"{"{"} {super().__str__()}, {self._proto}, {self._target}, " \
               + f"{self._pages}, {self._conn_max} {"}"}"


# CLIENT **********************************************************************


class Client(_Service):
    def __init__(self, cpu_limit: str = "0.5", mem_limit: str = "256M", 
                 disable_swap: bool = False, nameserver: str = "", forward: bool = False,
                 syn_cookie: SynCookieType = SynCookieType.enable, 
                 congestion_control: CongestionControlType = CongestionControlType.cubic):
        """
        @params:
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
            - nameserver: The IPv4 address.
            - forward: Enable or disable packet forwarding.
            - syn_cookie: Configure SYN cookies.
            - congestion_control: Configure congestion control.
        """

        super().__init__(_ServiceType.client, "client", cpu_limit, mem_limit, 
                         disable_swap, nameserver, forward, syn_cookie, congestion_control)


# SERVER **********************************************************************


class Server(_Service):
    def __init__(self, cpu_limit: str = "0.5", mem_limit: str = "256M", 
                 disable_swap: bool = False, nameserver: str = "", forward: bool = False,
                 syn_cookie: SynCookieType = SynCookieType.enable, 
                 congestion_control: CongestionControlType = CongestionControlType.cubic):
        """
        @params:
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
            - nameserver: The IPv4 address.
            - forward: Enable or disable packet forwarding.
            - syn_cookie: Configure SYN cookies.
            - congestion_control: Configure congestion control.
        """

        super().__init__(_ServiceType.server, "nginx", cpu_limit, mem_limit, 
                         disable_swap, nameserver, forward, syn_cookie, congestion_control)


# DHCP ************************************************************************


class DHCP(_Service):
    def __init__(self, lease_time: int = 600, cpu_limit: str = "0.5", mem_limit: str = "256M",
                 disable_swap: bool = False, nameserver: str = "", forward: bool = False, 
                 syn_cookie: SynCookieType = SynCookieType.enable,
                 congestion_control: CongestionControlType = CongestionControlType.cubic):
        """
        @params:
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
            - nameserver: The IPv4 address.
            - forward: Enable or disable packet forwarding.
            - syn_cookie: Configure SYN cookies.
            - congestion_control: Configure congestion control.
        WARNING:
            - The DHCP server is only configured for a single interface.
              Do not add multiple interfaces!
            - The DHCP server will advertise the nameserver.
        """

        super().__init__(_ServiceType.dhcp, "dhcp", cpu_limit, mem_limit, 
                         disable_swap, nameserver, forward, syn_cookie, congestion_control)
        
        assert(0 < lease_time)
        self._lease_time = lease_time

    def add_iface(self, iface: Iface, ip: str = "", gateway: str = "", lease_start: str = "", 
                  lease_end: str = "", firewall: FirewallType = FirewallType.none, 
                  drop_percent: int = 0, delay: int = 0) -> None:
        """
        @params:
            - iface: The network interface.
            - ip: The IPv4 address of the service.
            - gateway: The IPv4 address of the gateway.
            - lease_start: The IPv4 address at the start of the lease block.
            - lease_end: The IPv4 address at the end of the lease block.
            - firewall: Configure firewall.
            - drop_percent: Drop a percent of random traffic. From 0 to 100.
            - delay: Set a delay on traffic. In units of milliseconds.
        WARNING:
            - The default lease_start is .10; the default lease_end is .254
            - The DHCP server will advertise the gateway.
            - If the IP is empty, then the service will attempt to use DHCP
              for the IP, gateway, and nameserver.
        """

        # config default lease_start
        if lease_start == "":
            lease_start = _IPv4(iface._cidr._ip._int + 10)
            lease_start = lease_start._str

        # config default lease_end
        if lease_end == "":
            suffix_len = 32 - iface._cidr._prefix_len
            lease_end = _IPv4(iface._cidr._ip._int + 2 ** suffix_len - 2)
            lease_end = lease_end._str
        
        config = _IfaceConfig(iface, ip, gateway, firewall, drop_percent, delay,
                              lease_start, lease_end, NatType.none)
        self._iface_configs.append(config)


# ROUTER **********************************************************************


class Router(_Service):
    def __init__(self, ecmp: bool = False, cpu_limit: str = "0.5", mem_limit: str = "256M", 
                 disable_swap: bool = False, nameserver: str = "", forward: bool = True, 
                 syn_cookie: SynCookieType = SynCookieType.enable, 
                 congestion_control: CongestionControlType = CongestionControlType.cubic):
        """
        @params:
            - ecmp: Enable or disable ECMP.
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
            - nameserver: The IPv4 address.
            - forward: Enable or disable packet forwarding.
            - syn_cookie: Configure SYN cookies.
            - congestion_control: Configure congestion control.
        """

        super().__init__(_ServiceType.router, "nat", cpu_limit, mem_limit,
                         disable_swap, nameserver, forward, syn_cookie, congestion_control)
        
        self._ecmp = ecmp

    def add_iface(self, iface: Iface, ip: str = "", nat: NatType = NatType.none, 
                  gateway: str = "", firewall: FirewallType = FirewallType.none,
                  drop_percent: int = 0, delay: int = 0) -> None:
        """
        @params:
            - iface: The network interface.
            - ip: The IPv4 address of the service.
            - nat: Configure NAT.
            - gateway: The IPv4 address of the gateway.
            - firewall: Configure firewall.
            - drop_percent: Drop a percent of random traffic. From 0 to 100.
            - delay: Set a delay on traffic. In units of milliseconds.
        WARNING:
            - If the IP is empty, then the service will attempt to use DHCP
              for the IP, gateway, and nameserver.
        """

        config = _IfaceConfig(iface, ip, gateway, firewall, drop_percent, delay, "", "", nat)
        self._iface_configs.append(config)

    def __str__(self) -> str:
        return f"{"{"} {super().__str__()}, {self._ecmp} {"}"}"


# DNS *************************************************************************


class _Domain():
    def __init__(self, name: str, ip: str):
        """
        @params:
            - name: The domain name.
            - ip: The IPv4 address of the service.
        """

        assert(name != "")
        self._name = name

        assert(ip != "")
        self._ip = _IPv4(ip)

    def __str__(self) -> str:
        return f"{"{"} {self._name}, {self._ip._str} {"}"}"
    

class Nameserver(_Service):
    def __init__(self, ttl: int = 600, log: bool = False, cpu_limit: str = "0.5", 
                 mem_limit: str = "256M", disable_swap: bool = False, forward: bool = False, 
                 syn_cookie: SynCookieType = SynCookieType.enable, 
                 congestion_control: CongestionControlType = CongestionControlType.cubic):
        """
        @params:
            - ttl: The time-to-live for the resolved record in seconds.
            - log: Enable or disable logging of queries.
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
            - forward: Enable or disable packet forwarding.
            - syn_cookie: Configure SYN cookies.
            - congestion_control: Configure congestion control.
        """

        super().__init__(_ServiceType.dns, "dns", cpu_limit, mem_limit, disable_swap,
                         "", forward, syn_cookie, congestion_control)
        
        assert(ttl > 0)
        self._ttl = ttl

        self._log = log
        self._domains = []

    def register(self, name: str, ip: str) -> None:
        """
        @params:
            - name: The domain name.
            - ip: The IPv4 address of the service.
        """

        domain = _Domain(name, ip)
        self._domains.append(domain)

    def __str__(self) -> str:
        return f"{"{"} {super().__str__()}, {self._ttl}, {self._domains} {"}"}"
    