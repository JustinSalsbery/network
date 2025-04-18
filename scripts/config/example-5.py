
from src.components import *
from src.configurator import *


iface_0 = Iface("169.254.0.0/17")
iface_1 = Iface("169.254.128.0/17")

dhcp_0 = DHCP(nameserver="169.254.0.9")
dhcp_0.add_iface(iface_0, "169.254.0.2", "169.254.0.1")

dns_0 = Nameserver()
dns_0.add_iface(iface_0, ip="169.254.0.9")

client_0 = Client(nameserver="169.254.0.8")
client_0.add_iface(iface_0)

client_1 = Client()
client_1.add_iface(iface_0, gateway="169.254.0.8")

client_2 = Client()
client_2.add_iface(iface_0, "169.254.0.3")

client_3 = Client()
client_3.add_iface(iface_0, "169.254.0.4")

server_0 = Server()
server_0.add_iface(iface_0, ip="169.254.0.5")
dns_0.register("test.com", "169.254.0.5")

server_1 = Server()
server_1.add_iface(iface_0, ip="169.254.0.6")
dns_0.register("test.com", "169.254.0.6")

router_0 = Router()
router_0.add_iface(iface_0, "169.254.0.1")
router_0.add_iface(iface_1, "169.254.128.1")

client_4 = Client()
client_4.add_iface(iface_1, "169.254.128.5")

client_5 = Client()
client_5.add_iface(iface_1, "169.254.128.6")


conf = Configurator()
