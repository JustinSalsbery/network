
from src.components import *
from src.configurator import *


dns = DNS()
domain = dns.register("example-domain")

iface_1 = Iface("169.254.0.0/24")
iface_2 = Iface("169.254.1.0/24")

router = Router(True)
router.add_iface(iface_1, "169.254.0.1")
router.add_iface(iface_2, "169.254.1.1")

server_1 = Server()
server_1.add_iface(iface_1, "169.254.0.2")
domain.add_ip("169.254.0.2")

server_2 = Server()
server_2.add_iface(iface_1, "169.254.0.3")
domain.add_ip("169.254.0.3")

tgen = TrafficGenerator(domain)
tgen.add_iface(iface_2, "169.254.1.2", "169.254.1.1")

conf = Configurator()
