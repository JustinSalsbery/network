
from src.components import *
from src.configurator import *


iface_0 = Iface("100.0.0.0/24")

http_0 = HTTPServer()
http_0.add_iface(iface_0, ip="100.0.0.1")

client_0 = Client()
client_0.add_iface(iface_0, ip="100.0.0.2")

# REMOVE

iface_1 = Iface("100.0.1.0/24")
tgen_0 = TrafficGenerator("100.0.1.2")
tgen_0.add_iface(iface_1, "100.0.1.1")
lb_0 = LoadBalancer(["100.0.1.3", "100.0.1.4"])
lb_0.add_iface(iface_1, "100.0.1.2")
http_1 = HTTPServer()
http_1.add_iface(iface_1, "100.0.1.3")
http_2 = HTTPServer()
http_2.add_iface(iface_1, "100.0.1.4")

iface_2 = Iface("100.0.2.0/24")
lb_1 = LoadBalancer(["100.0.2.2", "100.0.2.3"])
lb_1.add_iface(iface_2, "100.0.2.1")
http_3 = HTTPServer()
http_3.add_iface(iface_2, "100.0.2.2")
http_4 = HTTPServer()
http_4.add_iface(iface_2, "100.0.2.3")


conf = Configurator()
