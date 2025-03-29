
from io import TextIOWrapper

from components import _comps
from components import *


SPACE = "  "

# networks:

#   a:
#     name: a
#     driver: bridge
#     internal: true
#     driver_opts:
#       com.docker.network.container_iface_prefix: a


# services:

#   nginx-1:
#     container_name: nginx-1
#     image: nginx
#     restart: unless-stopped
#     deploy:
#       resources:
#         limits:
#           cpus: 0.1
#           memory: 64M
#     memswap_limit: 64M
#     volumes:
#       - ./shared:/app/shared
#     networks:
#       - a
#     cap_add:
#       - NET_ADMIN
#     environment:
#       IFACES: a b c
#       SRC_IPS: 169.254.0.3 b c
#       NET_MASKS: a b c
#       GATEWAYS: 169.254.0.2 b c

#   locust:
#     container_name: locust
#     image: locust
#     restart: unless-stopped
#     deploy:
#       resources:
#         limits:
#           cpus: 0.1
#           memory: 64M
#     memswap_limit: 64M
#     volumes:
#       - ./shared:/app/shared
#     networks:
#       - b
#     cap_add:
#       - NET_ADMIN
#     environment:
#       # Routing configuration:
#       SRC_IP: 169.254.1.2
#       GATEWAY: 169.254.1.1
#       # Locust configuration:
#       DST_IP: 169.254.0.2
#       CONN_MAX: 800
#       CONN_RATE: 5
#       PROTO: http
#       PAGES: 40.html
#       WAIT_MIN: 5
#       WAIT_MAX: 15


class Configurator():
    def __init__(self):
        print(_comps["traffic_generator"][0])


# def __write_service(service: dict, file: TextIOWrapper):
#     if service["service_type"] == __ServiceType.server:
#         file.write(f"  {service["server_name"]}:\n")
#         file.write(f"    container_name: {service["server_name"]}\n")
#         file.write(f"    image: {service["server_type"].name}\n")
#         file.write("    restart: unless-stopped\n")
#         file.write("    deploy:\n")
#         file.write("      resources:\n")
#         file.write("        limits:\n")
#         file.write(f"          cpus: {service["cpu_limit"]}\n")
#         file.write(f"          memory: {service["mem_limit"]}\n")
#         file.write("    networks:\n")
#         file.write(f"      {service["network_name"]}:\n")
#         file.write(f"        ipv4_address: {service["server_ip"]}\n")
#         file.write("    volumes:\n")
#         file.write(f"      - ./shared:/app/shared\n")

#         if service["disable_swap"] == True:
#             file.write(f"    memswap_limit: {service["mem_limit"]}\n")

#     elif service["service_type"] == __ServiceType.traffic_generator:
#         file.write(f"  {service["generator_name"]}:\n")
#         file.write(f"    container_name: {service["generator_name"]}\n")
#         file.write(f"    image: {service["generator_type"].name}\n")
#         file.write("    restart: unless-stopped\n")
#         file.write("    deploy:\n")
#         file.write("      resources:\n")
#         file.write("        limits:\n")
#         file.write(f"          cpus: {service["cpu_limit"]}\n")
#         file.write(f"          memory: {service["mem_limit"]}\n")
#         file.write("    networks:\n")
#         file.write(f"      {service["network_name"]}:\n")
#         file.write(f"        ipv4_address: {service["generator_ip"]}\n")
#         file.write("    environment:\n")
#         file.write(f"      DESTINATION_IP: {service["destination_ip"]}\n")
#         file.write(f"      MAX_CONNECTIONS: {service["max_connections"]}\n")
#         file.write(f"      PROTOCOL: {service["protocol"].name}\n")
#         file.write(f"      PAGES: {service["pages"]}\n")
#         file.write(f"      WAIT_BETWEEN_PAGES_MIN: {service["wait_between_pages_min"]}\n")
#         file.write(f"      WAIT_BETWEEN_PAGES_MAX: {service["wait_between_pages_max"]}\n")
#         file.write(f"      RATE_OF_NEW_CONNECTIONS: {service["rate_of_new_connections"]}\n")
#         file.write("    volumes:\n")
#         file.write(f"      - ./shared:/app/shared\n")

#         if service["disable_swap"] == True:
#             file.write(f"    memswap_limit: {service["mem_limit"]}\n")


# # Write out the configuration as `docker-compose.yml`.
# # MUST be called for the configuration to be created.
# def write_conf():
#     with open("docker-compose.yml", "w") as file:

#         file.write("services:\n")
#         for service in __services:
#             __write_service(service, file)

#         # network MUST follow after services
#         # otherwise, docker compose down will fail

#         file.write("networks:\n")
#         for network in __networks:
#             file.write(f"  {network["network_name"]}:\n")
#             file.write(f"    name: {network["network_name"]}\n")
#             file.write("    ipam:\n")
#             file.write("      config:\n")
#             file.write(f"        - subnet: {network["network_subnet"]}\n")
#             file.write(f"          gateway: {network["network_gateway"]}\n")
                
#         file.write("\n")
