
from src.components import *
from src.configurator import *


iface_0 = Iface()
iface_1 = Iface()
iface_2 = Iface()

cidr_0 = "100.0.0.0/24"
cidr_1 = "100.0.1.0/24"
cidr_2 = "100.0.1.0/28"  # blackhole

router_0 = Router()
router_0.add_iface(iface_0, cidr=cidr_0, ip="100.0.0.1")
router_0.add_iface(iface_1, cidr=cidr_1, ip="100.0.1.1")
router_0.add_iface(iface_2, cidr=cidr_2, ip="100.0.1.2")

client_0 = Client()
client_0.add_iface(iface_0, cidr=cidr_0, ip="100.0.0.2", gateway="100.0.0.1")

http_0 = HTTPServer()  # will be blackholed
http_0.add_iface(iface_1, cidr=cidr_1, ip="100.0.1.15", gateway="100.0.1.1")

http_1 = HTTPServer()  # will not be blackholed
http_1.add_iface(iface_1, cidr=cidr_1, ip="100.0.1.16", gateway="100.0.1.1")


Configurator()
