
from src.components import *
from src.configurator import *


iface_0 = Iface("170.0.0.0/24")
iface_1 = Iface("170.0.1.0/24")
iface_2 = Iface("170.0.2.0/24")
iface_3 = Iface("169.254.0.0/24")
iface_4 = Iface("170.0.3.0/24")
iface_5 = Iface("169.254.1.0/24")
iface_6 = Iface("170.0.4.0/24")
iface_7 = Iface("170.0.5.0/24")

router_0 = Router()
router_0.add_iface(iface_0, "170.0.0.1")
router_0.add_iface(iface_1, "170.0.1.1")

router_1 = Router()
router_1.add_iface(iface_1, "170.0.1.2")
router_1.add_iface(iface_2, "170.0.2.1")
router_1.add_iface(iface_4, "170.0.3.1")

router_2 = Router()
router_2.add_iface(iface_2, "170.0.2.2")
router_2.add_iface(iface_3, "169.254.0.1")

router_3 = Router()
router_3.add_iface(iface_4, "170.0.3.2")
router_3.add_iface(iface_5, "169.254.5.1")
router_3.add_iface(iface_6, "170.0.4.1")

router_4 = Router()
router_4.add_iface(iface_6, "170.0.4.2")
router_4.add_iface(iface_7, "170.0.5.1")

client_0 = Client()
client_0.add_iface(iface_5, "169.254.1.2", "169.254.1.1")

client_1 = Client()
client_1.add_iface(iface_5, "169.254.1.3", "169.254.1.1")

client_2 = Client()
client_2.add_iface(iface_3, "169.254.0.2", "169.254.0.1")

client_3 = Client()
client_3.add_iface(iface_3, "169.254.0.3", "169.254.0.1")

server_0 = Server()
server_0.add_iface(iface_0, "170.0.0.2", "170.0.0.1")

server_1 = Server()
server_1.add_iface(iface_7, "170.0.5.2", "170.0.5.1")


conf = Configurator()
