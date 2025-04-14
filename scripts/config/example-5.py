
from src.components import *
from src.configurator import *


iface_0 = Iface("169.254.0.0/24")

client_0 = Client()
client_0.add_iface(iface_0)

client_0 = Client()
client_0.add_iface(iface_0)

dhcp_0 = DHCP()
dhcp_0.add_iface(iface_0, "169.254.0.1")


conf = Configurator()
