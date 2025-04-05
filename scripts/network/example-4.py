
from src.components import *
from src.configurator import *


iface_0 = Iface("169.254.0.0/24")
iface_1 = Iface("169.254.1.0/24")

client_0 = Client()
client_0.add_iface(iface_0, "169.254.0.2", "169.254.0.1", delay=100)
tgen_0 = TrafficGenerator("169.254.0.5", pages=["40.html"], congestion_control=CongestionControlType.cubic)
tgen_0.add_iface(iface_0, "169.254.0.3", "169.254.0.1", drop_percent=5)
tgen_1 = TrafficGenerator("169.254.0.5", pages=["40.html"], congestion_control=CongestionControlType.reno)
tgen_1.add_iface(iface_0, "169.254.0.4", "169.254.0.1", drop_percent=5)
server_0 = Server(syn_cookie=SynCookieType.disable)
server_0.add_iface(iface_0, "169.254.0.5", "169.254.0.1")

router_0 = Router()
router_0.add_iface(iface_0, "169.254.0.1")
router_0.add_iface(iface_1, "169.254.1.1")

client_1 = Client()
client_1.add_iface(iface_1, "169.254.1.2", "169.254.1.1", delay=100)
tgen_2 = TrafficGenerator("169.254.1.5", pages=["40.html"], congestion_control=CongestionControlType.cubic)
tgen_2.add_iface(iface_1, "169.254.1.3", "169.254.1.1", drop_percent=5)
tgen_3 = TrafficGenerator("169.254.1.5", pages=["40.html"], congestion_control=CongestionControlType.reno)
tgen_3.add_iface(iface_1, "169.254.1.4", "169.254.1.1", drop_percent=5)
server_1 = Server(syn_cookie=SynCookieType.force)
server_1.add_iface(iface_1, "169.254.1.5", "169.254.1.1")


conf = Configurator()
