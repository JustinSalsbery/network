
from src.components import *
from src.configurator import *


iface_0 = Iface("169.254.0.0/24")

server_0 = Server()
server_0.add_iface(iface_0, "169.254.0.1", rate=100)

client_0 = Client()
client_0.add_iface(iface_0, ip="169.254.0.2")


conf = Configurator()
