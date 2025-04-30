
from src.components import *
from src.configurator import *


iface_0 = Iface("169.254.0.0/16")

dns_0 = DNSServer()
dns_0.add_iface(iface_0, ip="169.254.0.8")

client_0 = Client(nameserver="169.254.0.8")  # client_0 uses dns_0
client_0.add_iface(iface_0, ip="169.254.0.3")

http_0 = HTTPServer()
http_0.add_iface(iface_0, "169.254.0.1")
dns_0.register("server-0", "169.254.0.1")  # add "server-0" domain to dns_0

dns_1 = DNSServer(nameservers=["169.254.0.8"])  # dns_1 will reference dns_0
dns_1.add_iface(iface_0, ip="169.254.0.9")    # for any domain unknown to dns_1

client_1 = Client(nameserver="169.254.0.9")  # client_1 uses dns_1
client_1.add_iface(iface_0, ip="169.254.0.4")

http_1 = HTTPServer()
http_1.add_iface(iface_0, "169.254.0.2")
dns_1.register("server-1", "169.254.0.2")  # add "server-1" domain to dns_1

# client_0 is able to resolve: "server-0"
# client_1 is able to resolve: "server-0", "server-1"

# dns can also be used for basic load balancing


conf = Configurator()
