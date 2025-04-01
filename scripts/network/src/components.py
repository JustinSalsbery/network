
from enum import Enum, auto
from random import choice


_comps = {} # Created components are registered here.


# IPv4 ************************************************************************


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

        else:
            print(f"error: Illegal IPv4 address {ip}")
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

    def __ip_to_int(self, ip: str) -> int:
        """
        @params:
            - ip: The IPv4 address as a string, ex. "169.254.0.0"
        @returns: The IPv4 as an integer, ex. 0x0a000001
        """

        octets = ip.split(".")
        octets = [*map(int, octets)]

        ip = octets[0] << 24 \
             + octets[1] << 16 \
             + octets[2] << 8 \
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
        self._is_private = self.__is_private(self._ip, self._prefix_len_int)

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

        octets = []

        while prefix_len > 0:
            bits = prefix_len

            if bits > 8:
                bits = 8

            prefix_len -= bits
            
            octet = 2 ** bits - 1
            octets.append(f"{octet}")

        while len(octets) < 4:
            octets.append("0")

        ip = ".".join(octets)
        return _IPv4(ip)
    
    def __is_private(self, ip: _IPv4, prefix_len: int, cidr: str) -> bool:
        """
        @params:
            - ip: The IPv4 object.
            - prefix_len: The prefix length.
            - cidr: The IPv4 as a string in CIDR notation, ex. "169.254.0.0/16"
        @returns: Whether the CIDR address is private or public.
        WARNING:
            - Subnets that straddle both public and private IP ranges are disallowed.
        """
        
        netmask = self.__netmask(prefix_len)

        # 10 /8
        is_private = self.__is_private_internal(prefix_len, 8, ip, 0x0a000000, 
                                                netmask, cidr)
        if is_private:
            return True

        # 169.254 /16
        is_private = self.__is_private_internal(prefix_len, 16, ip, 0xa9fe0000, 
                                                netmask, cidr)
        if is_private:
            return True

        # 172.16 /12
        is_private = self.__is_private_internal(prefix_len, 12, ip, 0xac100000, 
                                                netmask, cidr)
        if is_private:
            return True
        
        # 192.168 /16
        is_private = self.__is_private_internal(prefix_len, 16, ip, 0xc0a80000,
                                                netmask, cidr)
        if is_private:
            return True

        return False
    
    def __is_private_internal(self, prefix_len: int, prefix_len_private: int, ip: _IPv4,
                              ip_private: int, netmask: _IPv4, cidr: str) -> bool:
        """
        @params:
            - prefix_len: The prefix length.
            - prefix_len_private: The prefix length of the private network.
            - ip: The IPv4 object.
            - ip_private: The IPv4 address of the private network
            - netmask: The netmask.
            - cidr: The IPv4 as a string in CIDR notation, ex. "169.254.0.0/16"
        @return: Whether the CIDR address is private or public.
        """

        netmask_min = min(prefix_len, prefix_len_private)
        netmask_min = self.__netmask(netmask)

        if ip._ip_int & netmask_min._ip_int == ip_private & netmask_min._ip_int:
            if prefix_len < prefix_len_private:
                print("error: Illegal CIDR {cidr}")
                exit(1)

            return True
        return False
    
    def __str__(self) -> str:
        return f"{"{"} {self._cidr}, {self._ip}, {self._netmask}, {self._is_private} {"}"}"


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


class Iface():
    def __init__(self, cidr: str):
        """
        @params:
            - subnet: The IPv4 address in CIDR notation, ex. "169.254.1.0/24"
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
    def __init__(self, iface: Iface, src_ip: str, gateway: str, is_snat: bool):
        """
        @params:
            - iface: The network interface.
            - src_ip: The IPv4 address of the service.
            - gateway: The IPv4 address of the gateway.
            - is_snat: Enable or disable SNAT. Only implemented on routers.
        """

        self._iface = iface
        self._src = _IPv4(src_ip)
        self._gateway = _IPv4(gateway)
        self._is_snat = is_snat

    def __str__(self) -> str:
        return f"{"{"} {self._iface}, {self._src}, {self._gateway}, {self._is_snat} {"}"}"


# SERVICE *********************************************************************


class _ServiceType(Enum):
    server = auto()
    tgen = auto()  # traffic generator
    lb = auto()  # load balancer
    router = auto()
    client = auto()


class _Service():
    def __init__(self, type: _ServiceType, image: str, cpu_limit: str, mem_limit: str, 
                 disable_swap: bool, do_forward: bool):
        """
        @params:
            - type: The type of the service.
            - image: The name of the Docker image.
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
            - do_forward: Enable or disable packet forwarding.
        """

        self._type = type
        self._image = image
        self._cpu_limit = cpu_limit
        self._mem_limit = mem_limit
        self._disable_swap = disable_swap
        self._do_forward = do_forward

        name = type.name
        if name not in _comps:
            _comps[name] = []

        count = len(_comps[name])
        _comps[name].append(self)

        self._name = f"{name}-{count}"
        self._ifaces = []

    def add_iface(self, iface: Iface, src_ip: str, gateway: str = None, is_snat: bool = False) -> None:
        """
        @params:
            - iface: The network interface.
            - src_ip: The IPv4 address of the service.
            - gateway: The IPv4 address of the gateway.
            - is_snat: Enable or disable SNAT. Only implemented on routers.
        """

        config = _IfaceConfig(iface, src_ip, gateway, is_snat)
        self._ifaces.append(config)

    def __str__(self):
        return f"{"{"} {self._name}, {self._image}, {self._cpu_limit}, {self._mem_limit}, " \
               + f"{self._disable_swap}, {self._do_forward}, {self._ifaces} {"}"}"


# TRAFFIC GENERATOR ***********************************************************


class Protocol(Enum):
    http = auto()
    https = auto()


class TrafficGenerator(_Service):
    def __init__(self, target: _Domain | str, proto: Protocol = Protocol.http,
                 pages: list[str] = ["/"], conn_max: int = 500, conn_rate: int = 5, 
                 wait_min: float = 5, wait_max: float = 15, cpu_limit: str = "0.1", 
                 mem_limit: str = "64M", disable_swap: bool = False, 
                 do_forward: bool = False):
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
            - do_forward: Enable or disable packet forwarding.
        """

        super().__init__(_ServiceType.tgen, "locust", cpu_limit, mem_limit, 
                         disable_swap, do_forward)
        
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
        return f"{"{"} {super().__str__()}, {self._dst_ip}, {self._proto}, {self._pages}, " \
               + f"{self._conn_max}, {self._conn_rate}, {self._wait_min}, {self._wait_max} {"}"}"


# CLIENT **********************************************************************


class Client(_Service):
    def __init__(self, cpu_limit: str = "0.1", mem_limit: str = "64M", 
                 disable_swap: bool = False, do_forward: bool = False):
        """
        @params:
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
            - do_forward: Enable or disable packet forwarding.
        """

        super().__init__(_ServiceType.client, "client", cpu_limit, mem_limit, 
                         disable_swap, do_forward)


# SERVER **********************************************************************


class Server(_Service):
    def __init__(self, cpu_limit: str = "0.1", mem_limit: str = "64M", 
                 disable_swap: bool = False, do_forward: bool = False):
        """
        @params:
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
            - do_forward: Enable or disable packet forwarding.
        """

        super().__init__(_ServiceType.server, "nginx", cpu_limit, mem_limit, 
                         disable_swap, do_forward)


# ROUTER **********************************************************************


class Router(_Service):
    def __init__(self, cpu_limit: str = "0.1", mem_limit: str = "64M", disable_swap: bool = False, 
                 do_forward: bool = True):
        """
        @params:
            - do_nat: Enable or disable network address translation.
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
            - do_forward: Enable or disable packet forwarding.
        """

        super().__init__(_ServiceType.router, "nat", cpu_limit, mem_limit,
                         disable_swap, do_forward)

    def __str__(self) -> str:
        return f"{"{"} {super().__str__()}, {self._do_nat} {"}"}"
