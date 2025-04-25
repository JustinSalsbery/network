
from src.components import *
from src.configurator import *


iface_0 = Iface("169.254.0.0/16")

server_0 = Server()
server_0.add_iface(iface_0, "169.254.0.1")

client_0 = Client()
client_0.add_iface(iface_0, ip="169.254.0.2", rate=0.001)

tgen_0 = TrafficGenerator("169.254.0.1", pages=["/400.html"], conn_max=20)
tgen_0.add_iface(iface_0, "169.254.0.3")

tgen_1 = TrafficGenerator("169.254.0.1", pages=["/400.html"], conn_max=20, gzip=False)
tgen_1.add_iface(iface_0, "169.254.0.4")


conf = Configurator()
