
from src.components import *
from src.configurator import *


iface_0 = Iface()

dhcp_0 = DHCPServer()
dhcp_0.add_iface(iface_0, cidr="169.254.0.0/16", ip="169.254.0.1")

client_0 = Client()  # dchp sets the cidr and ip
client_0.add_iface(iface_0)

client_1 = Client()
client_1.add_iface(iface_0)


Configurator()
