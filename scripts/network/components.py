
from enum import Enum, auto
from subprocess import getstatusoutput


# NETWORK *********************************************************************


class Network():
    def __gateway(self, subnet: str) -> str:
        ip, prefix_len = subnet.split("/")
        ip = ip.split(".")

        assert(ip[3] == "0" and prefix_len != "32")

        ip[3] = "2"

        return ".".join(ip)

    def __init__(self, networks: list, subnet: str, nat: bool = True):
        """
        @params:
            - networks: A list of created networks.
            - subnet: The IP subnet in CIDR notation; ex. "169.254.1.0/24"
            - nat: Enable or disable Network Address Translation on the gateway.
        WARNING: 
            - NEITHER .1 nor .2 are valid addresses!
            - Docker automatically reserves .1 for the host machine.
              Non-internal networks use .1 as the default route allowing internet connectivity.
            - I automatically reserve .2 for a network router.
              .2 is set as the default gateway.
        """

        self.name = f"network-{len(networks)}"
        self.subnet = subnet
        self.gateway = self.__gateway(subnet)
        self.nat = nat

    def __str__(self) -> str:
        return f"{"{"} {self.name}, {self.subnet}, {self.gateway} {"}"}"


# SERVICE *********************************************************************


class ServiceType(Enum):
    server = auto()
    traffic_generator = auto()
    load_balancer = auto()


class Service():
    def __init__(self, type: ServiceType, image: str, name: str, network: Network, src_ip: str,
                 gateway: str, cpu_limit: str, mem_limit: str, disable_swap: bool):
        """
        @params:
            - type: The type of the service.
            - name: The name of the service.
            - network: The network the service is connected to.
            - src_ip: The IPv4 address of the service.
            - gateway: Defaults to the network gateway of .2
            - cpu_limit: Limit service cpu time; "0.1" is 10% of a logical core.
            - mem_limit: Limit service memory.
            - disable_swap: Enables/disables swap memory.
        """

        self.type = type
        self.name = name
        self.network = network
        self.src_ip = src_ip

        self.gateway = gateway
        if gateway == None:
            self.gateway = network.gateway

        self.cpu_limit = cpu_limit
        self.mem_limit = mem_limit
        self.disable_swap = disable_swap

    def __str__(self) -> str:
        return f"{"{"} {self.type.name}, {self.name}, {self.network}, {self.src_ip}, " \
               + f"{self.gateway}, {self.cpu_limit}, {self.mem_limit}, {self.disable_swap} {"}"}"


# DOMAIN NAME SYSTEM **********************************************************


class Domain():
    def __init__(self, name: str, private_key: list[str], public_key: list[str]):
        self.name = name
        self.private_key = private_key
        self.public_key = public_key

    def __str__(self) -> str:
        return f"{"{"} {self.name}, {self.private_key}, {self.public_key} {"}"}"


class DomainNameSystem():
    __domains = {}
    def __init__(self):
        return

    def register(self, name) -> None:
        if name in DomainNameSystem.__domains:
            print(f"error: Domain {name} registered multiple times.")
            exit(1)

        s, o = getstatusoutput("openssl req -x509 -nodes -days 365 -newkey rsa:2048 "
                               + "-keyout /tmp/private.key -out /tmp/public.crt "
                               + "-subj '/C=US/ST=Washington/L=Spokane/O=Eastern Washington "
                               + f"University/OU=Department of Computer Science/CN={name}'")
        if s != 0:
            print(f"error: openssl failed with error code {s}.")
            print(o)

            exit(1)
        
        private_key = getstatusoutput("cat /tmp/private.key")[1].split("\n")
        public_key = getstatusoutput("cat /tmp/public.crt")[1].split("\n")

        DomainNameSystem.__domains[name] = Domain(name, private_key, public_key)

    def get_domain(self, name) -> Domain:
        if name not in DomainNameSystem.__domains:
            print(f"error: Domain {name} not registered.")
            exit(1)

        return DomainNameSystem.__domains[name]


# TRAFFIC GENERATOR ***********************************************************


class Protocol(Enum):
    http = auto()
    https = auto()

# # Create a traffic generator container. Pages are comma separated.
# # Ex. create_traffic_generator("locust", "internal", "169.254.0.3", "169.254.0.2", pages="foo.html,bar.html")
# def create_traffic_generator(generator_name: str, network_name: str, generator_ip: str, 
#                              destination_ip: str, max_connections: int = 500,
#                              generator_type: TrafficGeneratorType = TrafficGeneratorType.locust,
#                              protocol: Protocol = Protocol.http, pages: str = "/",
#                              wait_between_pages_min: float = 5, wait_between_pages_max: float = 15,
#                              rate_of_new_connections: int = 5, cpu_limit: str = "0.1", 
#                              mem_limit: str = "64M", disable_swap: bool = False):
#     service = {"service_type": __ServiceType.traffic_generator, "generator_name": generator_name,
#                "network_name": network_name, "generator_ip": generator_ip, 
#                "destination_ip": destination_ip, "max_connections": max_connections,
#                "generator_type": generator_type, "protocol": protocol, "pages": pages,
#                "wait_between_pages_min": wait_between_pages_min,
#                "wait_between_pages_max": wait_between_pages_max,
#                "rate_of_new_connections": rate_of_new_connections,
#                "cpu_limit": cpu_limit, "mem_limit": mem_limit, "disable_swap": disable_swap}
#     __services.append(service)


class TrafficGenerator(Service):
    pass


# SERVER **********************************************************************


class Server(Service):
    def __init__(self, servers: list, network: Network, src_ip: str, domain: Domain = None, 
                 cpu_limit: str = "0.1", mem_limit: str = "64M", disable_swap: bool = False):
        """
        @params:
            - domain: 
        """
        super().__init__(ServiceType.server, "nginx", f"nginx-{len(servers)}", network, src_ip,
                         None, cpu_limit, mem_limit, disable_swap)
        self.domain = domain

    def __str__(self) -> str:
        return f"{"{"} {super().__str__()}, {self.domain} {"}"}"


# ROUTER **********************************************************************


# class Router(Service):
#     pass

