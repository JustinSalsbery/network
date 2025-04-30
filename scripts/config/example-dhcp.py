
from src.components import *
from src.configurator import *


iface_0 = Iface("169.254.0.0/16")

dhcp_0 = DHCPServer()  # if configured, nameserver and gateway will be sent to the dhcp client
dhcp_0.add_iface(iface_0, ip="169.254.0.1")

client_0 = Client()
client_0.add_iface(iface_0)

client_1 = Client()
client_1.add_iface(iface_0)


conf = Configurator()
