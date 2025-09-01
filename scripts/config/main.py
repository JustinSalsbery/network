
from src.components import *
from src.configurator import *


iface_0 = Iface("100.0.0.0/24")

http_0 = HTTPServer()
http_0.add_iface(iface_0, ip="100.0.0.1")

client_0 = Client()
client_0.add_iface(iface_0, ip="100.0.0.2")

dhcp_0 = DHCPServer()
dns_0 = DNSServer()
router_0 = Router()
tgen_0 = TrafficGenerator("100.0.0.1")
lb_0 = LoadBalancer(["100.0.0.1"])

conf = Configurator()
