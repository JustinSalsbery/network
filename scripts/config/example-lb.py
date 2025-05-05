
from src.components import *
from src.configurator import *


iface_0 = Iface("10.0.0.0/16")
iface_1 = Iface("11.0.0.0/16")

client_0 = Client()
client_0.add_iface(iface_0, ip="10.0.0.2", gateway="10.0.0.1")

router_0 = Router()
router_0.add_iface(iface_0, ip="10.0.0.1", nat=NatType.snat_input)
router_0.add_iface(iface_1, ip="11.0.0.1")

# Both L4 and L5 load balancers are acting as reverse proxies.
# Traffic will route from the client through the load balancer to the servers.
# Traffic will return from the servers through the load balancers to the client.

lb_0 = LoadBalancer(["11.0.0.3", "11.0.0.4", "11.0.0.5"])
lb_0.add_iface(iface_1, ip="11.0.0.2", gateway="11.0.0.1")

# The servers do not need a configured gateway as they will reply through
# the load balancer.

http_0 = HTTPServer()
http_0.add_iface(iface_1, ip="11.0.0.3")

http_1 = HTTPServer()
http_1.add_iface(iface_1, ip="11.0.0.4")

http_2 = HTTPServer()
http_2.add_iface(iface_1, ip="11.0.0.5")


# available range must not overlap with any IPs in the configuration
conf = Configurator(available_range="192.168.0.0/16")
