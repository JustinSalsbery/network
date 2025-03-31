
from src.components import *
from src.configurator import *


dns = DNS()
domain_0 = dns.register("example-domain")

iface_0 = Iface("169.254.0.0/24")

server_0 = Server()
server_0.add_iface(iface_0, "169.254.0.1")
domain_0.add_ip("169.254.0.1")

client_0 = Client()
client_0.add_iface(iface_0, "169.254.0.2")

tgen_0 = TrafficGenerator(domain_0, proto=Protocol.https, pages=["/", "40.html"],
                          conn_max=50, conn_rate=1, mem_limit="128M")
tgen_0.add_iface(iface_0, "169.254.0.3")


conf = Configurator()
