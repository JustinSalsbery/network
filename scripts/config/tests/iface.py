
from src.components import *
from src.configurator import *


client_0 = Client()

for i in range(256):
    iface = Iface()

    client_0.add_iface(
        iface,
        cidr=f"169.254.{i}.0/24",
        ip=f"169.254.{i}.1",
    )


Configurator()
