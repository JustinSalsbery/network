
from enum import Enum, auto
from random import choice


_comps = {} # Created components are registered here.


# IPv4 ************************************************************************


class _SubnetType(Enum):
    public = auto()
    private = auto()


class _IPv4():
    def __init__(self, ip: str | int):
        """
        @params:
            - ip: The IPv4 address.
        """

        if type(ip) == str:
            if not self.__is_legal(ip):
                print(f"error: Illegal IPv4 address {ip}")
                exit(1)
        
            self._ip_str = ip
            self._ip_int = self.__ip_to_int(ip)

        elif type(ip) == int:
            if ip < 0 or ip > 0xffffffff:
                print(f"error: Illegal IPv4 address {ip}")
                exit(1)

            self._ip_int = ip
            self._ip_str = self.__ip_to_str(ip)

        else:  # Gateway defaults to NoneType
            self._ip_str = "none"
            self._ip_int = 0

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

    def __ip_to_int(self, ip: str) -> int:
        """
        @params:
            - ip: The IPv4 address as a string, ex. "169.254.0.0"
        @returns: The IPv4 as an integer, ex. 0x0a000001
        """

        octets = ip.split(".")
        octets = [*map(int, octets)]

        ip = (octets[0] << 24) \
             + (octets[1] << 16) \
             + (octets[2] << 8) \
             + octets[3]
        
        return ip
    
    def __ip_to_str(self, ip: int) -> str:
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
        return f"{"{"} {self._ip_str} {"}"}"


class _CIDR():
    def __init__(self, cidr: str):
        """
        @params:
            - cidr: The IPv4 as a string in CIDR notation, ex. "169.254.0.0/16"
        """

        if not self.__is_legal(cidr):
            print(f"error: Illegal CIDR {cidr}")
            exit(1)

        self._cidr = cidr
        ip, prefix_len = cidr.split("/")

        self._ip = _IPv4(ip)
        self._prefix_len_str = prefix_len
        self._prefix_len_int = int(prefix_len)

        self._netmask = self.__netmask(self._prefix_len_int)
        self._subnet_type = self.__subnet_type(self._ip, self._prefix_len_int)

    def __is_legal(self, cidr: str) -> bool:
        """
        @params:
            - cidr: The IPv4 as a string in CIDR notation, ex. "169.254.0.0/16"
        @return: Whether the IPv4 address is legal CIDR notation.
        """

        try:
            ip, prefix_len = cidr.split("/")

            ip = _IPv4(ip)
            prefix_len = int(prefix_len)
        except Exception:
            return False

        if prefix_len < 0 or prefix_len > 32:
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
    
    def __subnet_type(self, ip: _IPv4, prefix_len: int) -> _SubnetType:
        """
        @params:
            - ip: The IPv4 object.
            - prefix_len: The prefix length.
        @returns: Whether the CIDR address is private or public.
        WARNING:
            - Subnets that straddle both public and private IP ranges are disallowed.
        """
        
        # 10 /8
        subnet_type = self.__subnet_type_internal(prefix_len, 8, ip, 0x0a000000)
        if subnet_type == _SubnetType.private:
            return subnet_type

        # 169.254 /16
        subnet_type = self.__subnet_type_internal(prefix_len, 16, ip, 0xa9fe0000)
        if subnet_type == _SubnetType.private:
            return subnet_type

        # 172.16 /12
        subnet_type = self.__subnet_type_internal(prefix_len, 12, ip, 0xac100000)
        if subnet_type == _SubnetType.private:
            return subnet_type
        
        # 192.168 /16
        subnet_type = self.__subnet_type_internal(prefix_len, 16, ip, 0xc0a80000)
        if subnet_type == _SubnetType.private:
            return subnet_type

        return _SubnetType.public
    
    def __subnet_type_internal(self, prefix_len: int, prefix_len_private: int, ip: _IPv4,
                              ip_private: int) -> _SubnetType:
        """
        @params:
            - prefix_len: The prefix length.
            - prefix_len_private: The prefix length of the private network.
            - ip: The IPv4 object.
            - ip_private: The IPv4 address of the private network
        @return: Whether the CIDR address is private or public.
        """

        prefix_len_min = min(prefix_len, prefix_len_private)
        netmask_min = self.__netmask(prefix_len_min)

        if ip._ip_int & netmask_min._ip_int == ip_private & netmask_min._ip_int:
            if prefix_len < prefix_len_private:
                print("error: Illegal CIDR {cidr}")
                exit(1)

            return _SubnetType.private
        return _SubnetType.public
    
    def __str__(self) -> str:
        return f"{"{"} {self._cidr}, {self._netmask}, {self._subnet_type} {"}"}"


# DOMAIN NAME SYSTEM **********************************************************


class _Domain():
    def __init__(self, name: str):
        """
        @params:
            - name: The domain name.
        """

        self._name = name
        self._ips = {}

    def add_ip(self, ip: str) -> None:
        """
        @params:
            - ip: The IPv4 address.
        """

        _IPv4(ip)  # check legality
        if ip not in self._ips:
            self._ips[ip] = True

    def get_ip(self) -> str:
        """
        @returns: Returns a random IP.
        """

        if len(self._ips) == 0:
            print(f"error: No IP registered for domain {self._name}.")
            exit(1)

        return choice([*self._ips.keys()])

    def __str__(self) -> str:
        return f"{"{"} {self._name}, {self._ips} {"}"}"


class DNS():
    _domains = {}

    def __init__(self):
        if "DNS" not in _comps:
            _comps["DNS"] = self

    def register(self, name: str) -> _Domain:
        """
        @params:
            - name: The domain name.
        @return: The registered domain.
        WARNING:
            - You can only register a domain name once!
        """

        if name in DNS._domains:
            print(f"error: Domain {name} registered multiple times.")
            exit(1)

        domain = _Domain(name)
        DNS._domains[name] = domain

        return domain

    def resolve(self, name: str) -> _Domain:
        """
        @params:
            - name: The domain name.
        @return: The resolved domain.
        """
        
        if name not in DNS._domains:
            print(f"error: Domain {name} not registered.")
            exit(1)

        return DNS._domains[name]
    
    def __str__(self) -> str:
        return f"{"{"} {self._domains} {"}"}"


# INTERFACE *******************************************************************


class FirewallType(Enum):
    none = auto()
    inbound = auto()
    outbound = auto()


class NatType(Enum):
    none = auto()
    snat = auto()
    

class Iface():
    def __init__(self, cidr: str):
        """
        @params:
            - cidr: The IPv4 address in CIDR notation, ex. "169.254.1.0/24"
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
    def __init__(self, iface: Iface, src_ip: str, gateway: str, firewall: FirewallType, nat: NatType):
        """
        @params:
            - iface: The network interface.
            - src_ip: The IPv4 address of the service.
            - gateway: The IPv4 address of the gateway.
            - firewall: Configure basic firewall.
            - nat: Configure NAT. Only implemented on routers.
        """

        self._iface = iface
        self._src = _IPv4(src_ip)
        self._gateway = _IPv4(gateway)
        self._firewall = firewall
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


class _Service():
    def __init__(self, type: _ServiceType, image: str, cpu_limit: str, mem_limit: str, 
                 disable_swap: bool, forward: bool):
        """
        @params:
            - type: The type of the service.
            - image: The name of the Docker image.
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
            - forward: Enable or disable packet forwarding.
        """

        self._type = type
        self._image = image
        self._cpu_limit = cpu_limit
        self._mem_limit = mem_limit
        self._disable_swap = disable_swap
        self._forward = forward

        name = type.name
        if name not in _comps:
            _comps[name] = []

        count = len(_comps[name])
        _comps[name].append(self)

        self._name = f"{name}-{count}"
        self._ifaces = []

    def add_iface(self, iface: Iface, src_ip: str, gateway: str = None, firewall: FirewallType = FirewallType.none, 
                  nat: NatType = NatType.none) -> None:
        """
        @params:
            - iface: The network interface.
            - src_ip: The IPv4 address of the service.
            - gateway: The IPv4 address of the gateway.
            - firewall: Configure basic firewall.
            - nat: Configure NAT. Only implemented on routers.
        """

        config = _IfaceConfig(iface, src_ip, gateway, firewall, nat)
        self._ifaces.append(config)

    def __str__(self):
        return f"{"{"} {self._name}, {self._image}, {self._ifaces} {"}"}"


# TRAFFIC GENERATOR ***********************************************************


class Protocol(Enum):
    http = auto()
    https = auto()


class TrafficGenerator(_Service):
    def __init__(self, target: _Domain | str, proto: Protocol = Protocol.http,
                 pages: list[str] = ["/"], conn_max: int = 500, conn_rate: int = 5, 
                 wait_min: float = 5, wait_max: float = 15, cpu_limit: str = "0.1", 
                 mem_limit: str = "64M", disable_swap: bool = False, 
                 forward: bool = False):
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
            - forward: Enable or disable packet forwarding.
        """

        super().__init__(_ServiceType.tgen, "locust", cpu_limit, mem_limit, 
                         disable_swap, forward)
        
        self._domain = None
        if type(target) == _Domain:
            self._domain = target
            target = target.get_ip()

        self._dst_ip = _IPv4(target)

        self._proto = proto.name
        self._pages = pages
        self._conn_max = conn_max
        self._conn_rate = conn_rate
        self._wait_min = wait_min
        self._wait_max = wait_max

    def __str__(self) -> str:
        return f"{"{"} {super().__str__()}, {self._dst_ip}, {self._proto}, " \
               + f"{self._pages}, {self._conn_max} {"}"}"


# CLIENT **********************************************************************


class Client(_Service):
    def __init__(self, cpu_limit: str = "0.1", mem_limit: str = "64M", 
                 disable_swap: bool = False, forward: bool = False):
        """
        @params:
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
            - forward: Enable or disable packet forwarding.
        """

        super().__init__(_ServiceType.client, "client", cpu_limit, mem_limit, 
                         disable_swap, forward)


# SERVER **********************************************************************


class Server(_Service):
    def __init__(self, cpu_limit: str = "0.1", mem_limit: str = "64M", 
                 disable_swap: bool = False, forward: bool = False):
        """
        @params:
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
            - forward: Enable or disable packet forwarding.
        """

        super().__init__(_ServiceType.server, "nginx", cpu_limit, mem_limit, 
                         disable_swap, forward)


# ROUTER **********************************************************************


class Router(_Service):
    def __init__(self, ecmp: bool = False, cpu_limit: str = "0.1", mem_limit: str = "64M", 
                 disable_swap: bool = False, forward: bool = True):
        """
        @params:
            - ecmp: Enable or disable ECMP.
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
            - forward: Enable or disable packet forwarding.
        """

        super().__init__(_ServiceType.router, "nat", cpu_limit, mem_limit,
                         disable_swap, forward)
        
        self._ecmp = ecmp

    def __str__(self) -> str:
        return f"{"{"} {super().__str__()}, {self._ecmp} {"}"}"
