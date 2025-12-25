
from src.components import *
from src.configurator import *


iface_0 = Iface()
iface_1 = Iface()
iface_2 = Iface()

cidr_0 = "10.0.0.0/8"
cidr_1 = "11.0.0.0/8"
cidr_2 = "12.0.0.0/8"

router_0 = Router()
router_0.add_iface(iface_0, cidr=cidr_0, ip="10.0.0.1", nat=NatType.snat_input)
router_0.add_iface(iface_1, cidr=cidr_1, ip="11.0.0.1")

router_1 = Router()
router_1.add_iface(iface_1, cidr=cidr_1, ip="11.0.0.2")
router_1.add_iface(iface_2, cidr=cidr_2, ip="12.0.0.1")

client_0 = Client()
client_0.add_iface(iface_0, cidr=cidr_0, ip="10.0.0.2", gateway="10.0.0.1")

# Both L4 and L5 load balancers are acting as reverse proxies.
# Traffic will route from the client through the load balancer to the servers.
# Traffic will return from the servers through the load balancers to the client.

lb_0 = LoadBalancer(backends=["12.0.0.3", "12.0.0.4", "12.0.0.5"])
lb_0.add_iface(iface_2, cidr=cidr_2, ip="12.0.0.2", gateway="12.0.0.1")

# Servers reply through the load balancer - no gateway is necessary.

http_0 = HTTPServer()
http_0.add_iface(iface_2, cidr=cidr_2, ip="12.0.0.3")

http_1 = HTTPServer()
http_1.add_iface(iface_2, cidr=cidr_2, ip="12.0.0.4")

http_2 = HTTPServer()
http_2.add_iface(iface_2, cidr=cidr_2, ip="12.0.0.5")


# Available range must not overlap with any IPs in the configuration
Configurator(available_range="192.168.0.0/16")
