
from enum import Enum, auto
from io import TextIOWrapper


__services = []

class __ServiceType(Enum):
    server = auto()
    traffic_generator = auto()
    load_balancer = auto()


# TRAFFIC GENERATION **********************************************************

class TrafficGeneratorType(Enum):
    locust = auto()

class Protocol(Enum):
    http = auto()
    https = auto()

# Create a traffic generator container. Pages are comma separated.
# Ex. create_traffic_generator("locust", "internal", "169.254.0.3", "169.254.0.2", pages="foo.html,bar.html")
def create_traffic_generator(generator_name: str, network_name: str, generator_ip: str, 
                             destination_ip: str, max_connections: int = 500,
                             generator_type: TrafficGeneratorType = TrafficGeneratorType.locust,
                             protocol: Protocol = Protocol.http, pages: str = "/",
                             wait_between_pages_min: float = 5, wait_between_pages_max: float = 15,
                             rate_of_new_connections: int = 5, cpu_limit: str = "0.1", 
                             mem_limit: str = "64M", disable_swap: bool = False):
    service = {"service_type": __ServiceType.traffic_generator, "generator_name": generator_name,
               "network_name": network_name, "generator_ip": generator_ip, 
               "destination_ip": destination_ip, "max_connections": max_connections,
               "generator_type": generator_type, "protocol": protocol, "pages": pages,
               "wait_between_pages_min": wait_between_pages_min,
               "wait_between_pages_max": wait_between_pages_max,
               "rate_of_new_connections": rate_of_new_connections,
               "cpu_limit": cpu_limit, "mem_limit": mem_limit, "disable_swap": disable_swap}
    __services.append(service)


# SERVER **********************************************************************

class ServerType(Enum): # must match the image name
    nginx = auto()
    apache = auto()


# Create a server container.
# Ex. create_server("nginx", "internal", "169.254.0.2", mem_limit="128M")
def create_server(server_name: str, network_name: str, server_ip: str, 
                  server_type: ServerType = ServerType.nginx, cpu_limit: str = "0.1", 
                  mem_limit: str = "64M", disable_swap: bool = False):
    service = {"service_type": __ServiceType.server, "server_name": server_name,
               "network_name": network_name, "server_ip": server_ip, "server_type": server_type,
               "cpu_limit": cpu_limit, "mem_limit": mem_limit, "disable_swap": disable_swap}
    __services.append(service)


# NETWORK *********************************************************************

__networks = []

# Create a network. The network is internal to Docker.
# Ex. create_network("internal", "169.254.0.0/16", "169.254.0.1")
def create_network(network_name: str, network_subnet: str, network_gateway: str):
    network = {"network_name": network_name, "network_subnet": network_subnet, 
               "network_gateway": network_gateway}
    __networks.append(network)


# OUTPUT **********************************************************************

def __write_service(service: dict, file: TextIOWrapper):
    if service["service_type"] == __ServiceType.server:
        file.write(f"  {service["server_name"]}:\n")
        file.write(f"    container_name: {service["server_name"]}\n")
        file.write(f"    image: {service["server_type"].name}\n")
        file.write("    restart: unless-stopped\n")
        file.write("    deploy:\n")
        file.write("      resources:\n")
        file.write("        limits:\n")
        file.write(f"          cpus: {service["cpu_limit"]}\n")
        file.write(f"          memory: {service["mem_limit"]}\n")
        file.write("    networks:\n")
        file.write(f"      {service["network_name"]}:\n")
        file.write(f"        ipv4_address: {service["server_ip"]}\n")
        file.write("    volumes:\n")
        file.write(f"      - ./shared:/app/shared\n")

        if service["disable_swap"] == True:
            file.write(f"    memswap_limit: {service["mem_limit"]}\n")

    elif service["service_type"] == __ServiceType.traffic_generator:
        file.write(f"  {service["generator_name"]}:\n")
        file.write(f"    container_name: {service["generator_name"]}\n")
        file.write(f"    image: {service["generator_type"].name}\n")
        file.write("    restart: unless-stopped\n")
        file.write("    deploy:\n")
        file.write("      resources:\n")
        file.write("        limits:\n")
        file.write(f"          cpus: {service["cpu_limit"]}\n")
        file.write(f"          memory: {service["mem_limit"]}\n")
        file.write("    networks:\n")
        file.write(f"      {service["network_name"]}:\n")
        file.write(f"        ipv4_address: {service["generator_ip"]}\n")
        file.write("    environment:\n")
        file.write(f"      DESTINATION_IP: {service["destination_ip"]}\n")
        file.write(f"      MAX_CONNECTIONS: {service["max_connections"]}\n")
        file.write(f"      PROTOCOL: {service["protocol"].name}\n")
        file.write(f"      PAGES: {service["pages"]}\n")
        file.write(f"      WAIT_BETWEEN_PAGES_MIN: {service["wait_between_pages_min"]}\n")
        file.write(f"      WAIT_BETWEEN_PAGES_MAX: {service["wait_between_pages_max"]}\n")
        file.write(f"      RATE_OF_NEW_CONNECTIONS: {service["rate_of_new_connections"]}\n")
        file.write("    volumes:\n")
        file.write(f"      - ./shared:/app/shared\n")

        if service["disable_swap"] == True:
            file.write(f"    memswap_limit: {service["mem_limit"]}\n")


# Write out the configuration as `docker-compose.yml`.
# MUST be called for the configuration to be created.
def write_conf():
    with open("docker-compose.yml", "w") as file:

        file.write("services:\n")
        for service in __services:
            __write_service(service, file)

        # network MUST follow after services
        # otherwise, docker compose down will fail

        file.write("networks:\n")
        for network in __networks:
            file.write(f"  {network["network_name"]}:\n")
            file.write(f"    name: {network["network_name"]}\n")
            file.write("    ipam:\n")
            file.write("      config:\n")
            file.write(f"        - subnet: {network["network_subnet"]}\n")
            file.write(f"          gateway: {network["network_gateway"]}\n")
                
        file.write("\n")
