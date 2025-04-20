
from src.components import *
from src.configurator import *


iface_0 = Iface("169.254.0.0/24")
iface_1 = Iface("169.254.1.0/24")

client_0 = Client(forward=True)
client_0.add_iface(iface_0, ip="169.254.0.1")
client_0.add_iface(iface_1, ip="169.254.1.1")

client_1 = Client()
client_1.add_iface(iface_0, ip="169.254.0.2", gateway="169.254.0.1")

server_0 = Server()
server_0.add_iface(iface_1, ip="169.254.1.2", gateway="169.254.1.1")


conf = Configurator()
