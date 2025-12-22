
from src.components import *
from src.configurator import *


# Most datacenters use a multi-layer load balancing architecture.

iface_0 = Iface()  # Client network.
iface_1 = Iface()
iface_2 = Iface()  # Datacenter network.
iface_3 = Iface()

cidr_0 = "192.168.0.0/16"
cidr_1 = "174.0.0.0/8"
cidr_2 = "192.168.0.0/16"
cidr_3 = "175.0.0.0/24"

client_0 = Client()
client_0.add_iface(iface_0, cidr=cidr_0, ip="192.168.0.2", gateway="192.168.0.1")

router_0 = Router(ecmp=ECMPType.l3)
router_0.add_iface(iface_0, cidr=cidr_0, ip="192.168.0.1", nat=NatType.snat_input)
router_0.add_iface(iface_1, cidr=cidr_1, ip="174.0.0.1")

# Instead of configuring static gateways, datacenters may use NAT.
# With NAT, traffic exiting the network is load balanced between routers.
# Note that NAT is stateful which creates another point of failure.

router_1 = Router(ecmp=ECMPType.l3)
router_1.add_iface(iface_1, cidr=cidr_1, ip="174.0.0.2")
router_1.add_iface(iface_2, cidr=cidr_2, ip="192.168.0.1", nat=NatType.snat_output)

router_2 = Router(ecmp=ECMPType.l3)
router_2.add_iface(iface_1, cidr=cidr_1, ip="174.0.0.3")
router_2.add_iface(iface_2, cidr=cidr_2, ip="192.168.0.2", nat=NatType.snat_output)

# Layer 4 load balancers:
# Many load balancers claim the same IP by, essentially, acting as a router.
# Each load balancer advertises a route and claims the same IP on said advertised route.
# Note that this requires an ECMP router.

backends = ["192.168.0.5", "192.168.0.6", "192.168.0.7", "192.168.0.8"]

lb_0 = LoadBalancer(backends=backends, type=LBType.l4, advertise=True)
lb_0.add_iface(iface_2, cidr=cidr_2, ip="192.168.0.3")
lb_0.add_iface(iface_3, cidr=cidr_3, ip="175.0.0.1")  # The IP address the client should address.

lb_1 = LoadBalancer(backends=backends, type=LBType.l4, advertise=True)
lb_1.add_iface(iface_2, cidr=cidr_2, ip="192.168.0.4")
lb_1.add_iface(iface_3, cidr=cidr_3, ip="175.0.0.1")

# Layer 5 load balancers:
# L5 load balancers are slower than L4 load balancers, so more are needed.

backends = ["192.168.0.9",  "192.168.0.10", "192.168.0.11", "192.168.0.12", 
            "192.168.0.13", "192.168.0.14", "192.168.0.15", "192.168.0.16"]

lb_2 = LoadBalancer(backends=backends)
lb_2.add_iface(iface_2, cidr=cidr_2, ip="192.168.0.5")

lb_3 = LoadBalancer(backends=backends)
lb_3.add_iface(iface_2, cidr=cidr_2, ip="192.168.0.6")

lb_4 = LoadBalancer(backends=backends)
lb_4.add_iface(iface_2, cidr=cidr_2, ip="192.168.0.7")

lb_5 = LoadBalancer(backends=backends)
lb_5.add_iface(iface_2, cidr=cidr_2, ip="192.168.0.8")

# Servers:

http_0 = HTTPServer()
http_0.add_iface(iface_2, cidr=cidr_2, ip="192.168.0.9", firewall=FirewallType.block_new_conn_output_strict)

http_1 = HTTPServer()
http_1.add_iface(iface_2, cidr=cidr_2, ip="192.168.0.10", firewall=FirewallType.block_new_conn_output_strict)

http_2 = HTTPServer()
http_2.add_iface(iface_2, cidr=cidr_2, ip="192.168.0.11", firewall=FirewallType.block_new_conn_output_strict)

http_3 = HTTPServer()
http_3.add_iface(iface_2, cidr=cidr_2, ip="192.168.0.12", firewall=FirewallType.block_new_conn_output_strict)

http_4 = HTTPServer()
http_4.add_iface(iface_2, cidr=cidr_2, ip="192.168.0.13", firewall=FirewallType.block_new_conn_output_strict)

http_5 = HTTPServer()
http_5.add_iface(iface_2, cidr=cidr_2, ip="192.168.0.14", firewall=FirewallType.block_new_conn_output_strict)

http_6 = HTTPServer()
http_6.add_iface(iface_2, cidr=cidr_2, ip="192.168.0.15", firewall=FirewallType.block_new_conn_output_strict)

http_7 = HTTPServer()
http_7.add_iface(iface_2, cidr=cidr_2, ip="192.168.0.16", firewall=FirewallType.block_new_conn_output_strict)


Configurator()
