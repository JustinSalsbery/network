
from src.components import *
from src.configurator import *


iface_0 = Iface()

dns_0 = DNSServer()
dns_0.add_iface(iface_0, cidr="169.254.0.0/16", ip="169.254.0.1")

client_0 = Client(dns_server="169.254.0.1")  # client_0 uses dns_0
client_0.add_iface(iface_0, cidr="169.254.0.0/16", ip="169.254.0.2")

http_0 = HTTPServer()
http_0.add_iface(iface_0, cidr="169.254.0.0/16", ip="169.254.0.3")
dns_0.register("server-0", "169.254.0.3")  # add "server-0" domain to dns_0


Configurator()
