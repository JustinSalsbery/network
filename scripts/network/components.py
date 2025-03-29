
from enum import Enum, auto
from random import choice


comps = {} # Created components are registered here. Used for unique naming.


# DOMAIN NAME SYSTEM **********************************************************


class Domain():
    def __init__(self, name: str):
        """
        @params:
            - name: The domain name.
        WARNING:
            - Do not call this function!
              DNS will call this function on your behalf.
        """

        self.name = name
        self.ips = {}

    def add_ip(self, ip: str) -> None:
        """
        @params:
            - ip: The IPv4 address.
        """

        if ip not in self.ips:
            self.ips[ip] = True

    def get_ip(self) -> str:
        """
        @returns: Returns a random IP.
        """

        if len(self.ips) == 0:
            print(f"error: No IP registered for domain {self.name}.")
            exit(1)

        return choice([*self.ips.keys()])

    def __str__(self) -> str:
        return f"{"{"} {self.name}, {self.ips} {"}"}"


class DNS():
    __domains = {}

    def __init__(self):
        return

    def register(self, name: str) -> Domain:
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

        domain = Domain(name)
        DNS.__domains[name] = domain

        return domain

    def resolve(self, name: str) -> Domain:
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

        if "Iface" not in comps:
            comps["Iface"] = 0
        
        count = comps["Iface"]
        comps["Iface"] += 1

        self.name = f"network-{count}"
        self.subnet = subnet

        self.ip, self.prefix_len = subnet.split("/")
        self.net_mask = self.__net_mask(self.prefix_len)

        self.gateway = None

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

    def add_gateway(self, src_ip: str) -> None:
        """
        @params:
            - gateway: The service to add as the gateway.
        WARNING:
            - Do not call this function!
              IfaceConfig will call this function on your behalf.
        """
        
        if self.gateway != None:
            print(f"error: Multiple defined gateways for network {self.name}.")
            exit(1)

        self.gateway = src_ip

    def __str__(self) -> str:
        return f"{"{"} {self.name}, {self.subnet}, {self.net_mask}, {self.gateway} {"}"}"


class IfaceConfig():
    def __init__(self, iface: Iface, src_ip: str, is_gateway: bool = False):
        """
        @params:
            - iface: The network interface.
            - src_ip: The IPv4 address.
            - is_gateway: IPs not within the network subnet are routed to the gateway.
        WARNING:
            - Each network may only have 1 network gateway!
        """

        self.iface = iface
        self.src_ip = src_ip

        self.is_gateway = is_gateway
        if is_gateway:
            iface.add_gateway(src_ip)

    def __str__(self) -> str:
        return f"{"{"} {self.iface}, {self.src_ip} {"}"}"


# SERVICE *********************************************************************


class ServiceType(Enum):
    server = auto()
    traffic_generator = auto()
    load_balancer = auto()
    router = auto()


class __Service():
    def __init__(self, type: ServiceType, image: str, cpu_limit: str, mem_limit: str, 
                 disable_swap: bool):
        """
        @params:
            - type: The type of the service.
            - image: The name of the Docker image.
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
        """

        self.type = type
        self.image = image
        self.cpu_limit = cpu_limit
        self.mem_limit = mem_limit
        self.disable_swap = disable_swap

        name = type.name
        if name not in comps:
            comps[name] = 0

        count = comps[name]
        comps[name] += 1

        self.name = f"{name}-{count}"
        self.ifaces = []

    def add_iface(self, iface_config: IfaceConfig) -> None:
        """
        @params:
            - iface_config: The configuration for the interface.
        """

        self.ifaces.append(iface_config)

    def __str__(self):
        return f"{"{"} {self.name}, {self.image}, {self.cpu_limit}, {self.mem_limit}, " \
               + f"{self.disable_swap}, {self.ifaces} {"}"}"


# TRAFFIC GENERATOR ***********************************************************


class Protocol(Enum):
    http = auto()
    https = auto()


class TrafficGenerator(__Service):
    def __init__(self, target: Domain | str, proto: Protocol = Protocol.http,
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

        super().__init__(ServiceType.traffic_generator, "locust", cpu_limit, 
                         mem_limit, disable_swap)
        
        self.dst_ip = target
        if type(target) == Domain:
            self.dst_ip = target.get_ip()

        self.proto = proto.name
        self.pages = pages
        self.conn_max = conn_max
        self.conn_rate = conn_rate
        self.wait_min = wait_min
        self.wait_max = wait_max


    def __str__(self) -> str:
        return f"{"{"} {super().__str__()}, {self.dst_ip}, {self.proto}, {self.pages}, " \
               + f"{self.conn_max}, {self.conn_rate}, {self.wait_min}, {self.wait_max} {"}"}"


# SERVER **********************************************************************


class Server(__Service):
    def __init__(self, cpu_limit: str = "0.1", mem_limit: str = "64M", disable_swap: bool = False):
        """
        @params:
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
        """

        super().__init__(ServiceType.server, "nginx", cpu_limit, mem_limit, disable_swap)


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

        super().__init__(ServiceType.router, "nat", cpu_limit, mem_limit, disable_swap)

        self.is_nat = is_nat
