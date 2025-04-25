
from src.components import *
from src.configurator import *


# larger networks need more time to establish routes

iface_0 = Iface("10.0.0.0/8")
iface_1 = Iface("10.0.0.0/8")  # networks may overlap
iface_2 = Iface("10.0.0.0/8")

iface_3 = Iface("11.0.0.0/16")
iface_4 = Iface("11.1.0.0/16")
iface_5 = Iface("11.2.0.0/16")
iface_6 = Iface("11.3.0.0/16")
iface_7 = Iface("11.4.0.0/16")
iface_8 = Iface("11.5.0.0/16")
iface_9 = Iface("11.6.0.0/16")
iface_10 = Iface("11.7.0.0/16")
iface_11 = Iface("11.8.0.0/16")
iface_12 = Iface("11.9.0.0/16")
iface_13 = Iface("11.10.0.0/16")
iface_14 = Iface("11.11.0.0/16")
iface_15 = Iface("11.12.0.0/16")

router_0 = Router(ecmp=True)
router_0.add_iface(iface_0, ip="10.0.0.1", nat=NatType.snat_input)
router_0.add_iface(iface_6, ip="11.3.0.1")

router_1 = Router(ecmp=True)
router_1.add_iface(iface_1, ip="10.0.0.1", nat=NatType.snat_input)
router_1.add_iface(iface_7, ip="11.4.0.1")

router_2 = Router(ecmp=True)
router_2.add_iface(iface_2, ip="10.0.0.1", nat=NatType.snat_input)
router_2.add_iface(iface_15, ip="11.12.0.1")

router_3 = Router(ecmp=True)
router_3.add_iface(iface_3, ip="11.0.0.1", nat=NatType.snat_output, firewall=FirewallType.block_new_conn_output_strict)
router_3.add_iface(iface_14, ip="11.11.0.1")

router_4 = Router(ecmp=True)
router_4.add_iface(iface_4, ip="11.1.0.1", firewall=FirewallType.block_new_conn_output_strict)
router_4.add_iface(iface_13, ip="11.10.0.1")

router_5 = Router(ecmp=True)
router_5.add_iface(iface_5, ip="11.2.0.1", firewall=FirewallType.block_new_conn_output_strict)
router_5.add_iface(iface_9, ip="11.6.0.1")

router_6 = Router(ecmp=True)
router_6.add_iface(iface_6, ip="11.3.0.2")
router_6.add_iface(iface_7, ip="11.4.0.2")
router_6.add_iface(iface_8, ip="11.5.0.1")

router_7 = Router(ecmp=True)
router_7.add_iface(iface_8, ip="11.5.0.2")
router_7.add_iface(iface_9, ip="11.6.0.2")
router_7.add_iface(iface_10, ip="11.7.0.1", cost=20)
router_7.add_iface(iface_11, ip="11.8.0.1")

router_8 = Router(ecmp=True)
router_8.add_iface(iface_10, ip="11.7.0.2", cost=20)
router_8.add_iface(iface_12, ip="11.9.0.1")
router_8.add_iface(iface_13, ip="11.10.0.2")
router_8.add_iface(iface_14, ip="11.11.0.2")

router_9 = Router(ecmp=True)
router_9.add_iface(iface_11, ip="11.8.0.2")
router_9.add_iface(iface_12, ip="11.9.0.2")
router_9.add_iface(iface_15, ip="11.12.0.2")

dns_0 = Nameserver()
dns_0.add_iface(iface_5, ip="11.2.0.2", gateway="11.2.0.1")

server_0 = Server()
server_0.add_iface(iface_4, ip="11.1.0.2", gateway="11.1.0.1")
dns_0.register("server-0.com", "11.1.0.2")

server_1 = Server()
server_1.add_iface(iface_4, ip="11.1.0.3", gateway="11.1.0.1")
dns_0.register("server-0.com", "11.1.0.3")  # dns load balancing

server_2 = Server()
server_2.add_iface(iface_4, ip="11.1.0.4", gateway="11.1.0.1")
dns_0.register("server-0.com", "11.1.0.4")

server_3 = Server()
server_3.add_iface(iface_3, ip="11.0.0.2")  # using snat rather than gateway
dns_0.register("server-1.com", "11.0.0.2")

dhcp_0 = DHCP(nameserver="11.2.0.2")
dhcp_0.add_iface(iface_0, ip="10.0.0.2", gateway="10.0.0.1")

client_0 = Client()
client_0.add_iface(iface_0)

tgen_0 = TrafficGenerator("server-0.com", requests=["/40.html"], conn_max=50)
tgen_0.add_iface(iface_0)

dhcp_1 = DHCP(nameserver="11.2.0.2")
dhcp_1.add_iface(iface_1, ip="10.0.0.2", gateway="10.0.0.1")

client_1 = Client()
client_1.add_iface(iface_1)

tgen_1 = TrafficGenerator("server-0.com", requests=["/40.html"], conn_max=50)
tgen_1.add_iface(iface_1)

dns_1 = Nameserver(log=True, nameservers=["11.2.0.2"])
dns_1.add_iface(iface_2, ip="10.0.0.3", gateway="10.0.0.1")

dhcp_2 = DHCP(nameserver="10.0.0.3")
dhcp_2.add_iface(iface_2, ip="10.0.0.2", gateway="10.0.0.1")

client_2 = Client()
client_2.add_iface(iface_2)

tgen_2 = TrafficGenerator("server-0.com", requests=["/40.html"], proto=Protocol.https, conn_max=20)
tgen_2.add_iface(iface_2)

server_4 = Server()
server_4.add_iface(iface_2, ip="10.0.0.4")
dns_1.register("server-2.com", "10.0.0.4")


# available range must not overlap with any IPs in the configuration
conf = Configurator(available_range="169.254.0.0/16")
