
from enum import Enum, auto
from random import choice


_comps = {} # Created components are registered here. Used for unique naming.


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
    __domains = {}

    def __init__(self):
        return

    def register(self, name: str) -> _Domain:
        """
        @params:
            - name: The domain name.
        @return: The registered domain.
        WARNING:
            - You can only register a domain name once!
        """

        if name in DNS.__domains:
            print(f"error: Domain {name} registered multiple times.")
            exit(1)

        domain = _Domain(name)
        DNS.__domains[name] = domain

        return domain

    def resolve(self, name: str) -> _Domain:
        """
        @params:
            - name: The domain name.
        @return: The resolved domain.
        """
        
        if name not in DNS.__domains:
            print(f"error: Domain {name} not registered.")
            exit(1)

        return DNS.__domains[name]
    
    def __str__(self) -> str:
        return f"{"{"} {self.__domains} {"}"}"


# INTERFACE *******************************************************************


class Iface():
    def __init__(self, subnet: str):
        """
        @params:
            - subnet: The IP subnet in CIDR notation; ex. "169.254.1.0/24"
        """

        if "Iface" not in _comps:
            _comps["Iface"] = 0
        
        count = _comps["Iface"]
        _comps["Iface"] += 1

        self._name = f"network-{count}"
        self._subnet = subnet

        self._ip, self._prefix_len = subnet.split("/")
        self._net_mask = self.__net_mask(self._prefix_len)

        self._gateway = None

    def __net_mask(self, prefix_len: str) -> str:
        """
        @params:
            - prefix_len: The prefix length of a subnet, ex. "24"
        @return: The network mask, ex. "255.255.255.0"
        """

        prefix_len = int(prefix_len)
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

        return ".".join(octets)

    def _add_gateway(self, src_ip: str) -> None:
        """
        @params:
            - gateway: The service to add as the gateway.
        """
        
        if self._gateway != None:
            print(f"error: Multiple defined gateways for network {self._name}.")
            exit(1)

        self._gateway = src_ip

    def __str__(self) -> str:
        return f"{"{"} {self._name}, {self._subnet}, {self._net_mask}, {self._gateway} {"}"}"


class _IfaceConfig():
    def __init__(self, iface: Iface, src_ip: str, is_gateway: bool = False):
        """
        @params:
            - iface: The network interface.
            - src_ip: The IPv4 address.
            - is_gateway: IPs not within the network subnet are routed to the gateway.
        """

        self._iface = iface
        self._src_ip = src_ip

        self._is_gateway = is_gateway
        if is_gateway:
            iface._add_gateway(src_ip)

    def __str__(self) -> str:
        return f"{"{"} {self.iface}, {self.src_ip} {"}"}"


# SERVICE *********************************************************************


class _ServiceType(Enum):
    server = auto()
    traffic_generator = auto()
    load_balancer = auto()
    router = auto()


class __Service():
    def __init__(self, type: _ServiceType, image: str, cpu_limit: str, mem_limit: str, 
                 disable_swap: bool):
        """
        @params:
            - type: The type of the service.
            - image: The name of the Docker image.
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
        """

        self._type = type
        self._image = image
        self._cpu_limit = cpu_limit
        self._mem_limit = mem_limit
        self._disable_swap = disable_swap

        name = type.name
        if name not in _comps:
            _comps[name] = 0

        count = _comps[name]
        _comps[name] += 1

        self._name = f"{name}-{count}"
        self._ifaces = []

    def add_iface(self, iface: Iface, src_ip: str, is_gateway: bool = False) -> None:
        """
        @params:
            - iface: The network interface.
            - src_ip: The IPv4 address.
            - is_gateway: IPs not within the network subnet are routed to the gateway.
        WARNING:
            - Each interface may only have 1 network gateway!
        """

        config = _IfaceConfig(iface, src_ip, is_gateway)
        self._ifaces.append(config)

    def __str__(self):
        return f"{"{"} {self._name}, {self._image}, {self._cpu_limit}, {self._mem_limit}, " \
               + f"{self._disable_swap}, {self._ifaces} {"}"}"


# TRAFFIC GENERATOR ***********************************************************


class Protocol(Enum):
    http = auto()
    https = auto()


class TrafficGenerator(__Service):
    def __init__(self, target: _Domain | str, proto: Protocol = Protocol.http,
                 pages: list[str] = ["/"], conn_max: int = 500, conn_rate: int = 5, 
                 wait_min: float = 5, wait_max: float = 15, cpu_limit: str = "0.1", 
                 mem_limit: str = "64M", disable_swap: bool = False):
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
            - disable_swap: Enables/disables swap memory.
        """

        super().__init__(_ServiceType.traffic_generator, "locust", cpu_limit, 
                         mem_limit, disable_swap)
        
        self._dst_ip = target
        if type(target) == _Domain:
            self._dst_ip = target.get_ip()

        self._proto = proto.name
        self._pages = pages
        self._conn_max = conn_max
        self._conn_rate = conn_rate
        self._wait_min = wait_min
        self._wait_max = wait_max


    def __str__(self) -> str:
        return f"{"{"} {super().__str__()}, {self._dst_ip}, {self._proto}, {self._pages}, " \
               + f"{self._conn_max}, {self._conn_rate}, {self._wait_min}, {self._wait_max} {"}"}"


# SERVER **********************************************************************


class Server(__Service):
    def __init__(self, cpu_limit: str = "0.1", mem_limit: str = "64M", disable_swap: bool = False):
        """
        @params:
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
        """

        super().__init__(_ServiceType.server, "nginx", cpu_limit, mem_limit, disable_swap)


# ROUTER **********************************************************************


class Router(__Service):
    def __init__(self, is_nat: bool, cpu_limit: str = "0.1", mem_limit: str = "64M", 
                 disable_swap: bool = False):
        """
        @params:
            - is_nat: Enable or disable network address translation.
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
        """

        super().__init__(_ServiceType.router, "nat", cpu_limit, mem_limit, disable_swap)

        self._is_nat = is_nat

    def __str__(self) -> str:
        return f"{"{"} {super().__str__()}, {self._is_nat} {"}"}"
