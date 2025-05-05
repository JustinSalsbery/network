
from src.components import *
from src.configurator import *


# Most datacenters use a 2-tier load balancing architecture.
# Layer 1 consists of L4 load balancers; Layer 2 consists of L5 load balancers.

iface_0 = Iface("192.168.0.0/16")  # Client network.
iface_1 = Iface("174.0.0.0/8")
iface_2 = Iface("175.0.0.0/16")  # Datacenter network.
iface_3 = Iface("175.0.1.0/24")  # The longest prefix is preferred.

client_0 = Client()
client_0.add_iface(iface_0, ip="192.168.0.2", gateway="192.168.0.1")

router_0 = Router(ecmp=ECMPType.l4)
router_0.add_iface(iface_0, ip="192.168.0.1", nat=NatType.snat_input)
router_0.add_iface(iface_1, ip="174.0.0.1")

# Instead of configuring static gateways, datacenters may use NAT.
# An extra benefit of using NAT is that traffic is load balanced between routers
# when exiting the network.

router_1 = Router(ecmp=ECMPType.l4)
router_1.add_iface(iface_1, ip="174.0.0.2")
router_1.add_iface(iface_2, ip="175.0.0.1", nat=NatType.snat_output)

router_2 = Router(ecmp=ECMPType.l4)
router_2.add_iface(iface_1, ip="174.0.0.3")
router_2.add_iface(iface_2, ip="175.0.0.2", nat=NatType.snat_output)

# Many load balancers may claim an IP by advertising identical an address space.
# Note that this requires an ECMP capable router.

lb_0 = LoadBalancer(backends=["175.0.0.5", "175.0.0.6", "175.0.0.7", "175.0.0.8"], 
                    type=LBType.l4, advertise=True)
lb_0.add_iface(iface_2, ip="175.0.0.3")
lb_0.add_iface(iface_3, ip="175.0.1.1")  # The IP address the client should address.

lb_1 = LoadBalancer(backends=["175.0.0.5", "175.0.0.6", "175.0.0.7", "175.0.0.8"], 
                    type=LBType.l4, advertise=True)
lb_1.add_iface(iface_2, ip="175.0.0.4")
lb_1.add_iface(iface_3, ip="175.0.1.1")

# L5 load balancers are slower than L4 load balancers, so more are needed.

backends = ["175.0.0.9", "175.0.0.10", "175.0.0.11", "175.0.0.12", 
            "175.0.0.13", "175.0.0.14", "175.0.0.15", "175.0.0.16"]

lb_2 = LoadBalancer(backends=backends)
lb_2.add_iface(iface_2, ip="175.0.0.5")

lb_3 = LoadBalancer(backends=backends)
lb_3.add_iface(iface_2, ip="175.0.0.6")

lb_4 = LoadBalancer(backends=backends)
lb_4.add_iface(iface_2, ip="175.0.0.7")

lb_5 = LoadBalancer(backends=backends)
lb_5.add_iface(iface_2, ip="175.0.0.8")

http_0 = HTTPServer()
http_0.add_iface(iface_2, ip="175.0.0.9")

http_1 = HTTPServer()
http_1.add_iface(iface_2, ip="175.0.0.10")

http_2 = HTTPServer()
http_2.add_iface(iface_2, ip="175.0.0.11")

http_3 = HTTPServer()
http_3.add_iface(iface_2, ip="175.0.0.12")

http_4 = HTTPServer()
http_4.add_iface(iface_2, ip="175.0.0.13")

http_5 = HTTPServer()
http_5.add_iface(iface_2, ip="175.0.0.14")

http_6 = HTTPServer()
http_6.add_iface(iface_2, ip="175.0.0.15")

http_7 = HTTPServer()
http_7.add_iface(iface_2, ip="175.0.0.16")


conf = Configurator()
