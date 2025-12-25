
from src.components import *
from src.configurator import *


iface_0 = Iface()
iface_1 = Iface()
iface_2 = Iface()
iface_3 = Iface()

# routers only advertise public networks
cidr_0 = "170.0.0.0/24"  # public
cidr_1 = "170.0.1.0/24"  # public
cidr_2 = "169.254.0.0/24"  # private; needs snat
cidr_3 = "169.254.1.0/24"  # private; needs snat

router_0 = Router()
router_0.add_iface(iface_0, cidr=cidr_0, ip="170.0.0.1")
router_0.add_iface(iface_1, cidr=cidr_1, ip="170.0.1.1")

router_1 = Router()
router_1.add_iface(iface_1, cidr=cidr_1, ip="170.0.1.2")
router_1.add_iface(iface_2, cidr=cidr_2, ip="169.254.0.1", nat=NatType.snat_input)
router_1.add_iface(iface_3, cidr=cidr_3, ip="169.254.1.1", nat=NatType.snat_input)

http_0 = HTTPServer()
http_0.add_iface(iface_0, cidr=cidr_0, ip="170.0.0.2", gateway="170.0.0.1")

dhcp_0 = DHCPServer()
dhcp_0.add_iface(iface_2, cidr=cidr_2, ip="169.254.0.2", gateway="169.254.0.1")

client_0 = Client()
client_0.add_iface(iface_2)

client_1 = Client()
client_1.add_iface(iface_2)

tgen_0 = TrafficGenerator(target="170.0.0.2")
tgen_0.add_iface(iface_3, cidr=cidr_3, ip="169.254.1.2", gateway="169.254.1.1")


Configurator()
