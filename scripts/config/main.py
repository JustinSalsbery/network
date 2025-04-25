
from src.components import *
from src.configurator import *


iface_0 = Iface("169.254.0.0/24")
iface_1 = Iface("169.254.1.0/24")

server_0 = Server()
server_0.add_iface(iface_0, "169.254.0.1", "169.254.0.200")

router_0 = Router()
router_0.add_iface(iface_0, ip="169.254.0.200", mtu=600)
router_0.add_iface(iface_1, ip="169.254.1.200", mtu=600)

client_0 = Client()
client_0.add_iface(iface_1, ip="169.254.1.2", rate=0.001)

tgen_0 = TrafficGenerator("169.254.0.1", requests=["/40.html", "/80.html"], conn_max=200)
tgen_0.add_iface(iface_1, "169.254.1.3", "169.254.1.200")

tgen_1 = TrafficGenerator("169.254.0.1", requests=["/40.html", "/80.html"], conn_max=200, gzip=False)
tgen_1.add_iface(iface_1, "169.254.1.4", "169.254.1.200")


conf = Configurator()
