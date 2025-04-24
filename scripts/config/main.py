
from src.components import *
from src.configurator import *


iface_0 = Iface("169.254.0.0/16")

dns_0 = Nameserver()
dns_0.add_iface(iface_0, ip="169.254.0.1")

dns_1 = Nameserver()
dns_1.add_iface(iface_0, ip="169.254.0.2")

dns_2 = Nameserver(nameservers=["169.254.0.1", "169.254.0.2"])
dns_2.add_iface(iface_0, ip="169.254.0.3")

dhcp_0 = DHCP(nameserver="169.254.0.3")
dhcp_0.add_iface(iface_0, ip="169.254.0.4")

client_0 = Client(nameserver="169.254.0.1")
client_0.add_iface(iface_0, ip="169.254.0.5")

client_1 = Client()
client_1.add_iface(iface_0)

server_0 = Server()
server_0.add_iface(iface_0, "169.254.0.6")
dns_0.register("server-0.com", "169.254.0.6")

server_1 = Server()
server_1.add_iface(iface_0, "169.254.0.7")
dns_1.register("server-1.com", "169.254.0.7")


conf = Configurator()
