
from src.components import *
from src.configurator import *


iface_0 = Iface()
iface_1 = Iface()
iface_2 = Iface()
iface_3 = Iface()
iface_4 = Iface()
iface_5 = Iface()
iface_6 = Iface()
iface_7 = Iface()

cidr_0 = "20.0.0.0/24"
cidr_1 = "20.1.0.0/24"
cidr_2 = "20.2.0.0/24"
cidr_3 = "20.3.0.0/24"
cidr_4 = "20.4.0.0/24"
cidr_5 = "20.5.0.0/24"
cidr_6 = "20.6.0.0/24"
cidr_7 = "20.7.0.0/24"

# network core

router_0 = Router()
router_0.add_iface(iface=iface_0, cidr=cidr_0, ip="20.0.0.1")
router_0.add_iface(iface=iface_1, cidr=cidr_1, ip="20.1.0.1")

tor_0 = TorNode()
tor_0.add_iface(iface=iface_0, cidr=cidr_0, ip="20.0.0.2", gateway="20.0.0.1")

router_1 = Router()
router_1.add_iface(iface=iface_1, cidr=cidr_1, ip="20.1.0.2")
router_1.add_iface(iface=iface_2, cidr=cidr_2, ip="20.2.0.1")

router_2 = Router()
router_2.add_iface(iface=iface_1, cidr=cidr_1, ip="20.1.0.3")
router_2.add_iface(iface=iface_3, cidr=cidr_3, ip="20.3.0.1")

# client

router_3 = Router()
router_3.add_iface(iface=iface_2, cidr=cidr_2, ip="20.2.0.2")
router_3.add_iface(iface=iface_4, cidr=cidr_4, ip="20.4.0.1")

client_0 = Client(tor_dir=tor_0)
client_0.add_iface(iface=iface_4, cidr=cidr_4, ip="20.4.0.2", gateway="20.4.0.1")

router_4 = Router()
router_4.add_iface(iface=iface_2, cidr=cidr_2, ip="20.2.0.3")
router_4.add_iface(iface=iface_5, cidr=cidr_5, ip="20.5.0.1")

tor_1 = TorNode(tor_dir=tor_0, is_exit=True)
tor_1.add_iface(iface=iface_5, cidr=cidr_5, ip="20.5.0.2", gateway="20.5.0.1")

tor_2 = TorNode(tor_dir=tor_0, is_exit=True)
tor_2.add_iface(iface=iface_5, cidr=cidr_5, ip="20.5.0.3", gateway="20.5.0.1")

tor_3 = TorNode(tor_dir=tor_0, is_exit=True)
tor_3.add_iface(iface=iface_5, cidr=cidr_5, ip="20.5.0.4", gateway="20.5.0.1")

# server

router_5 = Router()
router_5.add_iface(iface=iface_3, cidr=cidr_3, ip="20.3.0.2")
router_5.add_iface(iface=iface_6, cidr=cidr_6, ip="20.6.0.1")

tor_4 = TorNode(tor_dir=tor_0, is_bridge=True)
tor_4.add_iface(iface=iface_6, cidr=cidr_6, ip="20.6.0.2", gateway="20.6.0.1")

tor_5 = TorNode(tor_dir=tor_0)
tor_5.add_iface(iface=iface_6, cidr=cidr_6, ip="20.6.0.3", gateway="20.6.0.1")

tor_6 = TorNode(tor_dir=tor_0, is_exit=True)
tor_6.add_iface(iface=iface_6, cidr=cidr_6, ip="20.6.0.4", gateway="20.6.0.1")

router_6 = Router()
router_6.add_iface(iface=iface_3, cidr=cidr_3, ip="20.3.0.3")
router_6.add_iface(iface=iface_7, cidr=cidr_7, ip="20.7.0.1")

http_0 = HTTPServer(tor_dir=tor_0, tor_bridge=tor_4, tor_middle=tor_5, tor_exit=tor_6)
http_0.add_iface(iface=iface_7, cidr=cidr_7, ip="20.7.0.2", gateway="20.7.0.1")


Configurator()
