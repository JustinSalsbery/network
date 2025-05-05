
from src.components import *
from src.configurator import *


iface_0 = Iface("100.0.0.0/24")

client_0 = Client()
client_0.add_iface(iface_0, ip="100.0.0.1")


conf = Configurator()
