
from src.components import *
from src.configurator import *


iface_0 = Iface("100.0.0.0/24")
iface_1 = Iface("101.0.0.0/24")
iface_2 = Iface("102.0.0.0/24")

server_0 = Server()
server_0.add_iface(iface_0, "100.0.0.2", "100.0.0.1")

server_1 = Server()
server_1.add_iface(iface_0, "100.0.0.3", "100.0.0.1")

lb_0 = LoadBalancer(["100.0.0.2", "100.0.0.3"], type=LBType.l4)
lb_0.add_iface(iface_0, "100.0.0.4", "100.0.0.1")

lb_1 = LoadBalancer(["100.0.0.2", "100.0.0.3"], type=LBType.l4, algorithm=LBAlgorithm.source)
lb_1.add_iface(iface_0, "100.0.0.5", "100.0.0.1")

lb_2 = LoadBalancer(["100.0.0.2", "100.0.0.3"], type=LBType.l5)
lb_2.add_iface(iface_0, "100.0.0.6", "100.0.0.1")

lb_3 = LoadBalancer(["100.0.0.2", "100.0.0.3"], type=LBType.l5, algorithm=LBAlgorithm.source, advertise=iface_2)
lb_3.add_iface(iface_0, "100.0.0.7", "100.0.0.1")
lb_3.add_iface(iface_2, "102.0.0.1")

router_0 = Router(ecmp=ECMPType.l4)
router_0.add_iface(iface_0, "100.0.0.1")
router_0.add_iface(iface_1, "101.0.0.1")

client_0 = Client()
client_0.add_iface(iface_1, "101.0.0.2", "101.0.0.1")


conf = Configurator()
