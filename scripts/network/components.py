
from enum import Enum, auto
from random import choice


# NETWORK *********************************************************************


class Network():
    def __init__(self, networks: list, subnet: str):
        """
        @params:
            - networks: A list of created networks. Used for naming.
            - subnet: The IP subnet in CIDR notation; ex. "169.254.1.0/24"
        """

        self.name = f"network-{len(networks)}"
        self.subnet = subnet

        self.ip, self.prefix_len = subnet.split("/")
        self.network_mask = self.__network_mask(self.prefix_len)

        self.gateway = None

    def __network_mask(self, prefix_len: str) -> str:
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

    def add_gateway(self, gateway: str) -> None:
        """
        @params:
            - gateway: The IPv4 address of the gateway.
        WARNING:
            - Do not call this function!
              The service will call this function on your behalf.
        """
        if self.gateway != None:
            print(f"error: Multiple defined gateways for network {self.name}.")
            exit(1)

        self.gateway = gateway

    def __str__(self) -> str:
        return f"{"{"} {self.name}, {self.subnet}, {self.gateway} {"}"}"


class NetworkConfig():
    def __init__(self, network: Network, src_ip: str, is_gateway: bool = False, 
                 is_nat: bool = False):
        """
        @params:
            - network: The network interface.
            - src_ip: The IPv4 address of the container on the select network interface.
            - is_gateway: Only configured on the NAT Router image.
            - is_nat: Only implemented on the NAT Router image.
        WARNING:
            - Each network may only have 1 network gateway!
        """

        self.network = network
        self.src_ip = src_ip
        self.is_gateway = is_gateway
        self.is_nat = is_nat

    def __str__(self) -> str:
        return f"{"{"} {self.network}, {self.src_ip}, {self.is_gateway}, " \
               + f"{self.is_nat} {"}"}"


# SERVICE *********************************************************************


class ServiceType(Enum):
    server = auto()
    traffic_generator = auto()
    load_balancer = auto()
    router = auto()


class Service():
    def __init__(self, type: ServiceType, image: str, name: str, network_configs: list[NetworkConfig],
                 cpu_limit: str, mem_limit: str, disable_swap: bool):
        """
        @params:
            - type: The type of the service.
            - image: The name of the Docker image.
            - name: The name of the service.
            - network_configs: The network configurations for the container.
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
        """

        self.type = type
        self.image = image
        self.name = name

        self.network_configs = network_configs

        for config in network_configs:
            if config.is_gateway:
                config.network.add_gateway(config.src_ip)

        self.cpu_limit = cpu_limit
        self.mem_limit = mem_limit
        self.disable_swap = disable_swap

    def __str__(self) -> str:
        return f"{"{"} {self.type.name}, {self.image}, {self.name}, {self.network_configs}, " \
               + f"{self.cpu_limit}, {self.mem_limit}, {self.disable_swap} {"}"}"


# DOMAIN NAME SYSTEM **********************************************************


class Domain():
    def __init__(self, name: str):
        self.name = name
        self.ips = {}

    def add_ip(self, ip) -> None:
        """
        @params:
            - ip: The IPv4 address.
        WARNING:
            - Do not call this function!
              The server will call this function on your behalf.
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


class DomainNameSystem():
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
        if name in DomainNameSystem.__domains:
            print(f"error: Domain {name} registered multiple times.")
            exit(1)

        domain = Domain(name)
        DomainNameSystem.__domains[name] = domain

        return domain

    def resolve(self, name: str) -> Domain:
        """
        @params:
            - name: The domain name.
        @return: The resolved domain.
        """
        if name not in DomainNameSystem.__domains:
            print(f"error: Domain {name} not registered.")
            exit(1)

        return DomainNameSystem.__domains[name]
    
    def __str__(self) -> str:
        return f"{"{"} {self.__domains} {"}"}"


# TRAFFIC GENERATOR ***********************************************************


class Protocol(Enum):
    http = auto()
    https = auto()


class TrafficGenerator(Service):
    def __init__(self, traffic_generators: list, network: Network, src_ip: str, dst_ip: Domain | str, 
                 proto: Protocol = Protocol.http, pages: list[str] = ["/"], conn_max: int = 500, 
                 conn_rate: int = 5, wait_min: float = 5, wait_max: float = 15, cpu_limit: str = "0.1", 
                 mem_limit: str = "64M", disable_swap: bool = False):
        """
        @params:
            - traffic_generators: The list of created traffic generators. Used for naming.
            - network: The network interface.
            - src_ip: The IPv4 address of the container.
            - dst_ip: The IP address, or the domain, of the target server.
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

        super().__init__(ServiceType.traffic_generator, "locust", f"tgen-{len(traffic_generators)}",
                         [NetworkConfig(network, src_ip)], cpu_limit, mem_limit, disable_swap)
        
        self.dst_ip = dst_ip
        if type(dst_ip) == Domain:
            self.dst_ip = dst_ip.get_ip()

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


class Server(Service):
    def __init__(self, servers: list, network: Network, src_ip: str, domain: Domain = None, 
                 cpu_limit: str = "0.1", mem_limit: str = "64M", disable_swap: bool = False):
        """
        @params:
            - servers: The list of created servers. Used for naming.
            - network: The network interface.
            - src_ip: The IPv4 address of the container.
            - domain: The domain name.
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
        """
        super().__init__(ServiceType.server, "nginx", f"server-{len(servers)}", 
                         [NetworkConfig(network, src_ip)], cpu_limit, mem_limit, 
                         disable_swap)
        
        if domain != None:
            domain.add_ip(src_ip)

        self.domain = domain

    def __str__(self) -> str:
        return f"{"{"} {super().__str__()}, {self.domain} {"}"}"


# ROUTER **********************************************************************


class Router(Service):
    def __init__(self, routers: list, network_configs: list[NetworkConfig], cpu_limit: str = "0.1", 
                 mem_limit: str = "64M", disable_swap: bool = False):
        """
        @params:
            - routers: The list of created routers. Used for naming.
            - network_configs: The list of network configurations.
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
        """
        super().__init__(ServiceType.router, "nat", f"router-{len(routers)}", 
                         network_configs, cpu_limit, mem_limit, disable_swap)

    def __str__(self) -> str:
        return f"{"{"} {super().__str__()} {"}"}"
