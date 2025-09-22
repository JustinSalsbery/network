
from src.components import *
from src.configurator import *


# routers only advertise public networks
iface_0 = Iface("170.0.0.0/24")    # public
iface_1 = Iface("170.0.1.0/24")    # public
iface_2 = Iface("169.254.2.0/24")  # private
iface_3 = Iface("169.254.3.0/24")  # private

router_0 = Router()
router_0.add_iface(iface_0, ip="170.0.0.1")
router_0.add_iface(iface_1, ip="170.0.1.1")

router_1 = Router()
router_1.add_iface(iface_1, ip="170.0.1.2")
router_1.add_iface(iface_2, ip="169.254.2.1", nat=NatType.snat_input)
router_1.add_iface(iface_3, ip="169.254.3.1", nat=NatType.snat_input)

http_0 = HTTPServer()
http_0.add_iface(iface_0, ip="170.0.0.2", gateway="170.0.0.1")

dhcp_0 = DHCPServer()
dhcp_0.add_iface(iface_2, ip="169.254.2.2", gateway="169.254.2.1")

client_0 = Client()
client_0.add_iface(iface_2)

client_1 = Client()
client_1.add_iface(iface_2)

tgen_0 = TrafficGenerator("170.0.0.2")
tgen_0.add_iface(iface_3, ip="169.254.3.2", gateway="169.254.3.1")


conf = Configurator()
