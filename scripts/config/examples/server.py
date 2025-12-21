
from src.components import *
from src.configurator import *


iface_0 = Iface()

http_0 = HTTPServer()
http_0.add_iface(iface_0, cidr="100.0.0.0/24", ip="100.0.0.1")

client_0 = Client()
client_0.add_iface(iface_0, cidr="100.0.0.0/24", ip="100.0.0.2")


Configurator()
