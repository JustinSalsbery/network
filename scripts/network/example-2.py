
from src.components import *
from src.configurator import *


dns = DNS()
domain_0 = dns.register("example-domain")

iface_0 = Iface("169.254.0.0/24")
iface_1 = Iface("169.254.1.0/24")

router_0 = Router(True)
router_0.add_iface(iface_0, "169.254.0.1")
router_0.add_iface(iface_1, "169.254.1.1")

server_0 = Server()
server_0.add_iface(iface_0, "169.254.0.2")
domain_0.add_ip("169.254.0.2")

server_1 = Server()
server_1.add_iface(iface_0, "169.254.0.3")
domain_0.add_ip("169.254.0.3")

tgen_0 = TrafficGenerator(domain_0)
tgen_0.add_iface(iface_1, "169.254.1.2", "169.254.1.1")

conf = Configurator()
