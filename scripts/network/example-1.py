
from components import *
from configurator import *

iface_1 = Iface("169.254.0.0/24")
iface_2 = Iface("169.254.1.0/24")

router = Router(True)
router.add_iface(iface_1, "169.254.0.1", True)
router.add_iface(iface_2, "169.254.1.1", True)

server_1 = Server()
server_1.add_iface(iface_1, "169.254.0.2")

server_2 = Server()
server_2.add_iface(iface_1, "169.254.0.3")

tgen = TrafficGenerator("169.254.0.2")
tgen.add_iface(iface_2, "169.254.1.2")

Configurator()
