
from src.components import *
from src.configurator import *


iface_0 = Iface("100.0.0.0/24")
iface_1 = Iface("100.0.1.0/24")
iface_2 = Iface("100.0.2.0/24")
iface_3 = Iface("100.0.3.0/24")
iface_4 = Iface("100.0.4.0/24")
iface_5 = Iface("100.0.5.0/24")
iface_6 = Iface("100.0.2.0/28")  # blackhole

dns_0 = Nameserver()
dns_0.add_iface(iface_4, ip="100.0.4.2", gateway="100.0.4.1")

server_0 = Server()
server_0.add_iface(iface_2, ip="100.0.2.2", gateway="100.0.2.1")
dns_0.register("server", "100.0.2.2")  # will be blackholed

server_1 = Server()
server_1.add_iface(iface_2, ip="100.0.2.16", gateway="100.0.2.1")
dns_0.register("server", "100.0.2.16")  # will not be blackholed

client_0 = Client(nameserver="100.0.4.2")
client_0.add_iface(iface_0, ip="100.0.0.2", gateway="100.0.0.1")

router_0 = Router()
router_0.add_iface(iface_0, ip="100.0.0.1")
router_0.add_iface(iface_1, ip="100.0.1.1")
router_0.add_iface(iface_3, ip="100.0.3.1")

router_1 = Router()
router_1.add_iface(iface_1, ip="100.0.1.2")
router_1.add_iface(iface_2, ip="100.0.2.1")

router_2 = Router()
router_2.add_iface(iface_3, ip="100.0.3.2")
router_2.add_iface(iface_4, ip="100.0.4.1")
router_2.add_iface(iface_5, ip="100.0.5.1")

router_3 = Router()
router_3.add_iface(iface_5, ip="100.0.5.2")
router_3.add_iface(iface_6, ip="100.0.2.1")


conf = Configurator()
