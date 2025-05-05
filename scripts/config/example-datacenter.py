
from src.components import *
from src.configurator import *


# Most datacenters use a 2-tier load balancing architecture.
# Layer 1 consists of L4 load balancers; Layer 2 consists of L5 load balancers.

iface_0 = Iface("192.168.0.0/16")  # client network
iface_1 = Iface("170.0.0.0/8")     # server's public network
iface_2 = Iface("169.254.0.0/16")  # datacenter network

client_0 = Client()
client_0.add_iface(iface_0, ip="192.168.0.2", gateway="192.168.0.1")

router_0 = Router(ecmp=ECMPType.l4)
router_0.add_iface(iface_0, ip="192.168.0.1")
router_0.add_iface(iface_2, ip="169.254.0.1")

# These 2 load balancers are advertising their public interfaces allowing
# both load balancers to claim the same IP.
# Note that this requires an ECMP capable router.

lb_0 = LoadBalancer(backends=["169.254.0.4", "169.254.0.5", "169.254.0.6", "169.254.0.7"], 
                    type=LBType.l4, advertise=True)
lb_0.add_iface(iface_2, ip="169.254.0.2", gateway="169.254.0.1")
lb_0.add_iface(iface_1, ip="170.0.0.1")

lb_1 = LoadBalancer(backends=["169.254.0.4", "169.254.0.5", "169.254.0.6", "169.254.0.7"], 
                    type=LBType.l4, advertise=True)
lb_1.add_iface(iface_2, ip="169.254.0.3", gateway="169.254.0.1")
lb_1.add_iface(iface_1, ip="170.0.0.1")

# L5 load balancers are slower than L4 load balancers, so more are needed.
# None of these subsequent devices have a configured gateway. They must reply through
# the load balancer.

backends = ["169.254.0.8", "169.254.0.9", "169.254.0.10", "169.254.0.11",
            "169.254.0.12", "169.254.0.13", "169.254.0.14", "169.254.0.15"]

lb_2 = LoadBalancer(backends=backends)
lb_2.add_iface(iface_2, ip="169.254.0.4")

lb_3 = LoadBalancer(backends=backends)
lb_3.add_iface(iface_2, ip="169.254.0.5")

lb_4 = LoadBalancer(backends=backends)
lb_4.add_iface(iface_2, ip="169.254.0.6")

lb_5 = LoadBalancer(backends=backends)
lb_5.add_iface(iface_2, ip="169.254.0.7")

http_0 = HTTPServer()
http_0.add_iface(iface_2, ip="169.254.0.8")

http_1 = HTTPServer()
http_1.add_iface(iface_2, ip="169.254.0.9")

http_2 = HTTPServer()
http_2.add_iface(iface_2, ip="169.254.0.10")

http_3 = HTTPServer()
http_3.add_iface(iface_2, ip="169.254.0.11")

http_4 = HTTPServer()
http_4.add_iface(iface_2, ip="169.254.0.12")

http_5 = HTTPServer()
http_5.add_iface(iface_2, ip="169.254.0.13")

http_6 = HTTPServer()
http_6.add_iface(iface_2, ip="169.254.0.14")

http_7 = HTTPServer()
http_7.add_iface(iface_2, ip="169.254.0.15")


conf = Configurator()
