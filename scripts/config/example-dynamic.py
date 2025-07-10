
from src.components import *
from src.configurator import *


# DEFAULTS ********************************************************************

PROTOCOL = Protocol.http
REQUESTS = ["/40.html"]
WAIT_MIN = 5
WAIT_MAX = 5
CONN_RATE = 20
CONN_MAX = 1000
CPU_LIMIT = 0.3  # backbone routers use double this limit
MEM_LIMIT = 256

DNS_SERVER_ROOT = ["1.0.0.254"]  # each home group has an DNS server that references this root DNS server

# BACKBONE ROUTER 0 ***********************************************************

id_br = 0

iface_br_0a = Iface(f"1.{id_br}.0.0/16")  # backbone; internal connections
iface_br_0b = Iface(f"2.{id_br}.0.0/16")  # external connections
iface_br_b = iface_br_0b

router_br_0a = Router(ecmp=ECMPType.l3, cpu_limit=CPU_LIMIT * 2, mem_limit=MEM_LIMIT)
router_br_0a.add_iface(iface_br_0a, ip=f"1.{id_br}.0.1")
router_br_0a.add_iface(iface_br_b, ip=f"2.{id_br}.0.1")
router_br_0b = Router(ecmp=ECMPType.l3, cpu_limit=CPU_LIMIT * 2, mem_limit=MEM_LIMIT)
router_br_0b.add_iface(iface_br_0a, ip=f"1.{id_br}.0.2")
router_br_0b.add_iface(iface_br_b, ip=f"2.{id_br}.0.2")

dns_root = DNSServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
dns_root.add_iface(iface_br_0a, ip=f"1.{id_br}.0.254", gateway=f"1.{id_br}.0.1")



# HOME_GROUP = 5
# for i in range(HOME_GROUP):
#     iface_hg_0 = Iface(f"170.{id_hg}.0.0/16")
#     iface_hg = iface_hg_0

#     router_hg_0 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
#     router_hg_0.add_iface(iface_hg, ip=f"170.{id_hg}.0.1")
#     router_hg_0.add_iface(iface_br_b, ip=f"2.{id_br}.0.3")
#     dns_hg_0 = DNSServer(dns_servers=DNS_SERVER_ROOT, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
#     dns_hg_0.add_iface(iface_hg, ip=f"170.{id_hg}.0.2", gateway=f"170.{id_hg}.0.1")

# HOME GROUP 0 ****************************************************************

id_hg = 0

iface_hg_0 = Iface(f"170.{id_hg}.0.0/16")
iface_hg = iface_hg_0

router_hg_0 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_hg_0.add_iface(iface_hg, ip=f"170.{id_hg}.0.1")
router_hg_0.add_iface(iface_br_b, ip=f"2.{id_br}.0.3")
dns_hg_0 = DNSServer(dns_servers=DNS_SERVER_ROOT, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
dns_hg_0.add_iface(iface_hg, ip=f"170.{id_hg}.0.2", gateway=f"170.{id_hg}.0.1")

# HOME 0 **********************************************************************

iface_h_0 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_0

router_h_0 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_0.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_0.add_iface(iface_hg, ip=f"170.{id_hg}.0.3")

tgen_h_0a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_0a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_0b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_0b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 1 **********************************************************************

iface_h_1 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_1

router_h_1 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_1.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_1.add_iface(iface_hg, ip=f"170.{id_hg}.0.4")

tgen_h_1a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_1a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_1b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_1b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 2 **********************************************************************

iface_h_2 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_2

router_h_2 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_2.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_2.add_iface(iface_hg, ip=f"170.{id_hg}.0.5")

tgen_h_2a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_2a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_2b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_2b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 3 **********************************************************************

iface_h_3 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_3

router_h_3 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_3.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_3.add_iface(iface_hg, ip=f"170.{id_hg}.0.6")

tgen_h_3a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_3a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_3b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_3b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 4 **********************************************************************

iface_h_4 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_4

router_h_4 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_4.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_4.add_iface(iface_hg, ip=f"170.{id_hg}.0.7")

tgen_h_4a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_4a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_4b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_4b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME GROUP 1 ****************************************************************

id_hg = 1

iface_hg_1 = Iface(f"170.{id_hg}.0.0/16")
iface_hg = iface_hg_1

router_hg_1 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_hg_1.add_iface(iface_hg, ip=f"170.{id_hg}.0.1")
router_hg_1.add_iface(iface_br_b, ip=f"2.{id_br}.0.4")
dns_hg_1 = DNSServer(dns_servers=DNS_SERVER_ROOT, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
dns_hg_1.add_iface(iface_hg, ip=f"170.{id_hg}.0.2", gateway=f"170.{id_hg}.0.1")

# HOME 5 **********************************************************************

iface_h_5 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_5

router_h_5 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_5.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_5.add_iface(iface_hg, ip=f"170.{id_hg}.0.3")

tgen_h_5a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_5a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_5b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_5b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 6 **********************************************************************

iface_h_6 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_6

router_h_6 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_6.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_6.add_iface(iface_hg, ip=f"170.{id_hg}.0.4")

tgen_h_6a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_6a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_6b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_6b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 7 **********************************************************************

iface_h_7 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_7

router_h_7 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_7.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_7.add_iface(iface_hg, ip=f"170.{id_hg}.0.5")

tgen_h_7a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_7a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_7b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_7b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 8 **********************************************************************

iface_h_8 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_8

router_h_8 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_8.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_8.add_iface(iface_hg, ip=f"170.{id_hg}.0.6")

tgen_h_8a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_8a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_8b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_8b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 9 **********************************************************************

iface_h_9 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_9

router_h_9 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_9.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_9.add_iface(iface_hg, ip=f"170.{id_hg}.0.7")

tgen_h_9a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_9a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_9b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_9b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME GROUP 2 ****************************************************************

id_hg = 2

iface_hg_2 = Iface(f"170.{id_hg}.0.0/16")
iface_hg = iface_hg_2

router_hg_2 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_hg_2.add_iface(iface_hg, ip=f"170.{id_hg}.0.1")
router_hg_2.add_iface(iface_br_b, ip=f"2.{id_br}.0.5")
dns_hg_2 = DNSServer(dns_servers=DNS_SERVER_ROOT, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
dns_hg_2.add_iface(iface_hg, ip=f"170.{id_hg}.0.2", gateway=f"170.{id_hg}.0.1")

# HOME 10 *********************************************************************

iface_h_10 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_10

router_h_10 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_10.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_10.add_iface(iface_hg, ip=f"170.{id_hg}.0.3")

tgen_h_10a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_10a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_10b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_10b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 11 *********************************************************************

iface_h_11 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_11

router_h_11 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_11.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_11.add_iface(iface_hg, ip=f"170.{id_hg}.0.4")

tgen_h_11a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_11a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_11b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_11b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 12 *********************************************************************

iface_h_12 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_12

router_h_12 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_12.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_12.add_iface(iface_hg, ip=f"170.{id_hg}.0.5")

tgen_h_12a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_12a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_12b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_12b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 13 *********************************************************************

iface_h_13 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_13

router_h_13 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_13.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_13.add_iface(iface_hg, ip=f"170.{id_hg}.0.6")

tgen_h_13a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_13a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_13b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_13b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 14 *********************************************************************

iface_h_14 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_14

router_h_14 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_14.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_14.add_iface(iface_hg, ip=f"170.{id_hg}.0.7")

tgen_h_14a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_14a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_14b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_14b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME GROUP 3 ****************************************************************

id_hg = 3

iface_hg_3 = Iface(f"170.{id_hg}.0.0/16")
iface_hg = iface_hg_3

router_hg_3 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_hg_3.add_iface(iface_hg, ip=f"170.{id_hg}.0.1")
router_hg_3.add_iface(iface_br_b, ip=f"2.{id_br}.0.6")
dns_hg_3 = DNSServer(dns_servers=DNS_SERVER_ROOT, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
dns_hg_3.add_iface(iface_hg, ip=f"170.{id_hg}.0.2", gateway=f"170.{id_hg}.0.1")

# HOME 15 *********************************************************************

iface_h_15 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_15

router_h_15 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_15.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_15.add_iface(iface_hg, ip=f"170.{id_hg}.0.3")

tgen_h_15a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_15a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_15b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_15b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 16 *********************************************************************

iface_h_16 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_16

router_h_16 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_16.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_16.add_iface(iface_hg, ip=f"170.{id_hg}.0.4")

tgen_h_16a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_16a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_16b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_16b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 17 *********************************************************************

iface_h_17 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_17

router_h_17 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_17.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_17.add_iface(iface_hg, ip=f"170.{id_hg}.0.5")

tgen_h_17a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_17a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_17b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_17b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 18 *********************************************************************

iface_h_18 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_18

router_h_18 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_18.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_18.add_iface(iface_hg, ip=f"170.{id_hg}.0.6")

tgen_h_18a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_18a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_18b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_18b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 19 *********************************************************************

iface_h_19 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_19

router_h_19 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_19.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_19.add_iface(iface_hg, ip=f"170.{id_hg}.0.7")

tgen_h_19a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_19a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_19b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_19b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME GROUP 4 ****************************************************************

id_hg = 4

iface_hg_4 = Iface(f"170.{id_hg}.0.0/16")
iface_hg = iface_hg_4

router_hg_4 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_hg_4.add_iface(iface_hg, ip=f"170.{id_hg}.0.1")
router_hg_4.add_iface(iface_br_b, ip=f"2.{id_br}.0.7")
dns_hg_4 = DNSServer(dns_servers=DNS_SERVER_ROOT, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
dns_hg_4.add_iface(iface_hg, ip=f"170.{id_hg}.0.2", gateway=f"170.{id_hg}.0.1")

# HOME 20 *********************************************************************

iface_h_20 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_20

router_h_20 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_20.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_20.add_iface(iface_hg, ip=f"170.{id_hg}.0.3")

tgen_h_20a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_20a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_20b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_20b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 21 *********************************************************************

iface_h_21 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_21

router_h_21 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_21.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_21.add_iface(iface_hg, ip=f"170.{id_hg}.0.4")

tgen_h_21a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_21a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_21b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_21b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 22 *********************************************************************

iface_h_22 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_22

router_h_22 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_22.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_22.add_iface(iface_hg, ip=f"170.{id_hg}.0.5")

tgen_h_22a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_22a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_22b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_22b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 23 *********************************************************************

iface_h_23 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_23

router_h_23 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_23.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_23.add_iface(iface_hg, ip=f"170.{id_hg}.0.6")

tgen_h_23a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_23a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_23b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_23b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 24 *********************************************************************

iface_h_24 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_24

router_h_24 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_24.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_24.add_iface(iface_hg, ip=f"170.{id_hg}.0.7")

tgen_h_24a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_24a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_24b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_24b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME GROUP 5 ****************************************************************

id_hg = 5

iface_hg_5 = Iface(f"170.{id_hg}.0.0/16")
iface_hg = iface_hg_5

router_hg_5 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_hg_5.add_iface(iface_hg, ip=f"170.{id_hg}.0.1")
router_hg_5.add_iface(iface_br_b, ip=f"2.{id_br}.0.8")
dns_hg_5 = DNSServer(dns_servers=DNS_SERVER_ROOT, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
dns_hg_5.add_iface(iface_hg, ip=f"170.{id_hg}.0.2", gateway=f"170.{id_hg}.0.1")

# HOME 25 *********************************************************************

iface_h_25 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_25

router_h_25 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_25.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_25.add_iface(iface_hg, ip=f"170.{id_hg}.0.3")

tgen_h_25a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_25a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_25b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_25b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 26 *********************************************************************

iface_h_26 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_26

router_h_26 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_26.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_26.add_iface(iface_hg, ip=f"170.{id_hg}.0.4")

tgen_h_26a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_26a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_26b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_26b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 27 *********************************************************************

iface_h_27 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_27

router_h_27 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_27.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_27.add_iface(iface_hg, ip=f"170.{id_hg}.0.5")

tgen_h_27a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_27a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_27b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_27b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 28 *********************************************************************

iface_h_28 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_28

router_h_28 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_28.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_28.add_iface(iface_hg, ip=f"170.{id_hg}.0.6")

tgen_h_28a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_28a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_28b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_28b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 29 *********************************************************************

iface_h_29 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_29

router_h_29 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_29.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_29.add_iface(iface_hg, ip=f"170.{id_hg}.0.7")

tgen_h_29a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_29a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_29b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_29b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME GROUP 6 ****************************************************************

id_hg = 6

iface_hg_6 = Iface(f"170.{id_hg}.0.0/16")
iface_hg = iface_hg_6

router_hg_6 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_hg_6.add_iface(iface_hg, ip=f"170.{id_hg}.0.1")
router_hg_6.add_iface(iface_br_b, ip=f"2.{id_br}.0.9")
dns_hg_6 = DNSServer(dns_servers=DNS_SERVER_ROOT, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
dns_hg_6.add_iface(iface_hg, ip=f"170.{id_hg}.0.2", gateway=f"170.{id_hg}.0.1")

# HOME 30 *********************************************************************

iface_h_30 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_30

router_h_30 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_30.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_30.add_iface(iface_hg, ip=f"170.{id_hg}.0.3")

tgen_h_30a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_30a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_30b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_30b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 31 *********************************************************************

iface_h_31 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_31

router_h_31 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_31.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_31.add_iface(iface_hg, ip=f"170.{id_hg}.0.4")

tgen_h_31a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_31a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_31b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_31b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 32 *********************************************************************

iface_h_32 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_32

router_h_32 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_32.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_32.add_iface(iface_hg, ip=f"170.{id_hg}.0.5")

tgen_h_32a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_32a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_32b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_32b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 33 *********************************************************************

iface_h_33 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_33

router_h_33 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_33.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_33.add_iface(iface_hg, ip=f"170.{id_hg}.0.6")

tgen_h_33a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_33a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_33b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_33b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 34 *********************************************************************

iface_h_34 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_34

router_h_34 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_34.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_34.add_iface(iface_hg, ip=f"170.{id_hg}.0.7")

tgen_h_34a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_34a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_34b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_34b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME GROUP 7 ****************************************************************

id_hg = 7

iface_hg_7 = Iface(f"170.{id_hg}.0.0/16")
iface_hg = iface_hg_7

router_hg_7 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_hg_7.add_iface(iface_hg, ip=f"170.{id_hg}.0.1")
router_hg_7.add_iface(iface_br_b, ip=f"2.{id_br}.0.10")
dns_hg_7 = DNSServer(dns_servers=DNS_SERVER_ROOT, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
dns_hg_7.add_iface(iface_hg, ip=f"170.{id_hg}.0.2", gateway=f"170.{id_hg}.0.1")

# HOME 35 *********************************************************************

iface_h_35 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_35

router_h_35 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_35.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_35.add_iface(iface_hg, ip=f"170.{id_hg}.0.3")

tgen_h_35a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_35a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_35b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_35b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 36 *********************************************************************

iface_h_36 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_36

router_h_36 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_36.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_36.add_iface(iface_hg, ip=f"170.{id_hg}.0.4")

tgen_h_36a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_36a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_36b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_36b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 37 *********************************************************************

iface_h_37 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_37

router_h_37 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_37.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_37.add_iface(iface_hg, ip=f"170.{id_hg}.0.5")

tgen_h_37a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_37a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_37b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_37b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 38 *********************************************************************

iface_h_38 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_38

router_h_38 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_38.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_38.add_iface(iface_hg, ip=f"170.{id_hg}.0.6")

tgen_h_38a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_38a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_38b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_38b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 39 *********************************************************************

iface_h_39 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_39

router_h_39 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_39.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_39.add_iface(iface_hg, ip=f"170.{id_hg}.0.7")

tgen_h_39a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_39a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_39b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_39b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME GROUP 8 ****************************************************************

id_hg = 8

iface_hg_8 = Iface(f"170.{id_hg}.0.0/16")
iface_hg = iface_hg_8

router_hg_8 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_hg_8.add_iface(iface_hg, ip=f"170.{id_hg}.0.1")
router_hg_8.add_iface(iface_br_b, ip=f"2.{id_br}.0.11")
dns_hg_8 = DNSServer(dns_servers=DNS_SERVER_ROOT, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
dns_hg_8.add_iface(iface_hg, ip=f"170.{id_hg}.0.2", gateway=f"170.{id_hg}.0.1")

# HOME 40 *********************************************************************

iface_h_40 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_40

router_h_40 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_40.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_40.add_iface(iface_hg, ip=f"170.{id_hg}.0.3")

tgen_h_40a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_40a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_40b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_40b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 41 *********************************************************************

iface_h_41 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_41

router_h_41 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_41.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_41.add_iface(iface_hg, ip=f"170.{id_hg}.0.4")

tgen_h_41a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_41a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_41b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_41b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 42 *********************************************************************

iface_h_42 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_42

router_h_42 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_42.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_42.add_iface(iface_hg, ip=f"170.{id_hg}.0.5")

tgen_h_42a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_42a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_42b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_42b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 43 *********************************************************************

iface_h_43 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_43

router_h_43 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_43.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_43.add_iface(iface_hg, ip=f"170.{id_hg}.0.6")

tgen_h_43a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_43a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_43b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_43b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 44 *********************************************************************

iface_h_44 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_44

router_h_44 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_44.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_44.add_iface(iface_hg, ip=f"170.{id_hg}.0.7")

tgen_h_44a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_44a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_44b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_44b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME GROUP 9 ****************************************************************

id_hg = 9

iface_hg_9 = Iface(f"170.{id_hg}.0.0/16")
iface_hg = iface_hg_9

router_hg_9 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_hg_9.add_iface(iface_hg, ip=f"170.{id_hg}.0.1")
router_hg_9.add_iface(iface_br_b, ip=f"2.{id_br}.0.12")
dns_hg_9 = DNSServer(dns_servers=DNS_SERVER_ROOT, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
dns_hg_9.add_iface(iface_hg, ip=f"170.{id_hg}.0.2", gateway=f"170.{id_hg}.0.1")

# HOME 45 *********************************************************************

iface_h_45 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_45

router_h_45 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_45.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_45.add_iface(iface_hg, ip=f"170.{id_hg}.0.3")

tgen_h_45a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_45a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_45b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_45b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 46 *********************************************************************

iface_h_46 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_46

router_h_46 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_46.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_46.add_iface(iface_hg, ip=f"170.{id_hg}.0.4")

tgen_h_46a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_46a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_46b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_46b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 47 *********************************************************************

iface_h_47 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_47

router_h_47 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_47.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_47.add_iface(iface_hg, ip=f"170.{id_hg}.0.5")

tgen_h_47a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_47a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_47b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_47b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 48 *********************************************************************

iface_h_48 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_48

router_h_48 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_48.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_48.add_iface(iface_hg, ip=f"170.{id_hg}.0.6")

tgen_h_48a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_48a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_48b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_48b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# HOME 49 *********************************************************************

iface_h_49 = Iface("172.16.0.0/12")

target = "TODO"
iface = iface_h_49

router_h_49 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_h_49.add_iface(iface, ip="172.16.0.1", nat=NatType.snat_input)
router_h_49.add_iface(iface_hg, ip=f"170.{id_hg}.0.7")

tgen_h_49a = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_49a.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")
tgen_h_49b = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                            conn_max=CONN_MAX, conn_rate=CONN_RATE, wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                            dns_server=f"170.{id_hg}.0.2", cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
tgen_h_49b.add_iface(iface, ip="172.16.0.3", gateway="172.16.0.1")

# BACKBONE ROUTER 1 ***********************************************************

id_br = 1

iface_br_1a = Iface(f"1.{id_br}.0.0/16")  # backbone; internal connections
iface_br_1b = Iface(f"2.{id_br}.0.0/16")  # external connections
iface_br_b = iface_br_1b

router_br_1a = Router(ecmp=ECMPType.l3, cpu_limit=CPU_LIMIT * 2, mem_limit=MEM_LIMIT)
router_br_1a.add_iface(iface_br_1a, ip=f"1.{id_br}.0.1")
router_br_1a.add_iface(iface_br_b, ip=f"2.{id_br}.0.1")
router_br_1b = Router(ecmp=ECMPType.l3, cpu_limit=CPU_LIMIT * 2, mem_limit=MEM_LIMIT)
router_br_1b.add_iface(iface_br_1a, ip=f"1.{id_br}.0.2")
router_br_1b.add_iface(iface_br_b, ip=f"2.{id_br}.0.2")

router_br_1a.add_iface(iface_br_0a, ip=f"1.{id_br - 1}.0.3")  # connect to previous backbone
router_br_1b.add_iface(iface_br_0a, ip=f"1.{id_br - 1}.0.4")

# SERVER GROUP 0 **************************************************************

id_sg = 0

iface_sg_0 = Iface(f"180.{id_sg}.0.0/16")
iface_sg = iface_sg_0

router_sg_0 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_sg_0.add_iface(iface_sg, ip=f"180.{id_sg}.0.1")
router_sg_0.add_iface(iface_br_b, ip=f"2.{id_br}.0.3")

# DNS SERVER 0 ****************************************************************

id_s = 0

iface_s_0 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_0

router_s_0 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_0.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_0.add_iface(iface, ip=f"180.{id_sg}.0.2")

http_s_0a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_0a.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")
http_s_0b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_0b.add_iface(iface, ip=f"182.{id_s}.0.3", gateway=f"182.{id_s}.0.1")
http_s_0c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_0c.add_iface(iface, ip=f"182.{id_s}.0.4", gateway=f"182.{id_s}.0.1")

dns_root.register(f"dns-server-{id_s}", f"182.{id_s}.0.2")
dns_root.register(f"dns-server-{id_s}", f"182.{id_s}.0.3")
dns_root.register(f"dns-server-{id_s}", f"182.{id_s}.0.4")

# DNS SERVER 1 ****************************************************************

id_s = 1

iface_s_1 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_1

router_s_1 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_1.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_1.add_iface(iface, ip=f"180.{id_sg}.0.3")

http_s_1a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_1a.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")
http_s_1b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_1b.add_iface(iface, ip=f"182.{id_s}.0.3", gateway=f"182.{id_s}.0.1")
http_s_1c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_1c.add_iface(iface, ip=f"182.{id_s}.0.4", gateway=f"182.{id_s}.0.1")

dns_root.register(f"dns-server-{id_s}", f"182.{id_s}.0.2")
dns_root.register(f"dns-server-{id_s}", f"182.{id_s}.0.3")
dns_root.register(f"dns-server-{id_s}", f"182.{id_s}.0.4")

# DNS SERVER 2 ****************************************************************

id_s = 2

iface_s_2 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_2

router_s_2 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_2.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_2.add_iface(iface, ip=f"180.{id_sg}.0.4")

http_s_2a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_2a.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")
http_s_2b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_2b.add_iface(iface, ip=f"182.{id_s}.0.3", gateway=f"182.{id_s}.0.1")
http_s_2c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_2c.add_iface(iface, ip=f"182.{id_s}.0.4", gateway=f"182.{id_s}.0.1")

dns_root.register(f"dns-server-{id_s}", f"182.{id_s}.0.2")
dns_root.register(f"dns-server-{id_s}", f"182.{id_s}.0.3")
dns_root.register(f"dns-server-{id_s}", f"182.{id_s}.0.4")

# DNS SERVER 3 ****************************************************************

id_s = 3

iface_s_3 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_3

router_s_3 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_3.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_3.add_iface(iface, ip=f"180.{id_sg}.0.5")

http_s_3a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_3a.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")
http_s_3b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_3b.add_iface(iface, ip=f"182.{id_s}.0.3", gateway=f"182.{id_s}.0.1")
http_s_3c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_3c.add_iface(iface, ip=f"182.{id_s}.0.4", gateway=f"182.{id_s}.0.1")

dns_root.register(f"dns-server-{id_s}", f"182.{id_s}.0.2")
dns_root.register(f"dns-server-{id_s}", f"182.{id_s}.0.3")
dns_root.register(f"dns-server-{id_s}", f"182.{id_s}.0.4")

# DNS SERVER 4 ****************************************************************

id_s = 4

iface_s_4 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_4

router_s_4 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_4.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_4.add_iface(iface, ip=f"180.{id_sg}.0.6")

http_s_4a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_4a.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")
http_s_4b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_4b.add_iface(iface, ip=f"182.{id_s}.0.3", gateway=f"182.{id_s}.0.1")
http_s_4c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_4c.add_iface(iface, ip=f"182.{id_s}.0.4", gateway=f"182.{id_s}.0.1")

dns_root.register(f"dns-server-{id_s}", f"182.{id_s}.0.2")
dns_root.register(f"dns-server-{id_s}", f"182.{id_s}.0.3")
dns_root.register(f"dns-server-{id_s}", f"182.{id_s}.0.4")

# SERVER GROUP 1 **************************************************************

id_sg = 1

iface_sg_1 = Iface(f"180.{id_sg}.0.0/16")
iface_sg = iface_sg_1

router_sg_1 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_sg_1.add_iface(iface_sg, ip=f"180.{id_sg}.0.1")
router_sg_1.add_iface(iface_br_b, ip=f"2.{id_br}.0.4")

# ANYCAST SERVER 5 ************************************************************

id_s = 5

iface_s_5 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_5

router_s_5 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_5.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_5.add_iface(iface_sg, ip=f"180.{id_sg}.0.2")

iface_s_5a = Iface(f"182.{id_s}.1.0/24")
iface_s_5b = Iface(f"182.{id_s}.1.0/24")
iface_s_5c = Iface(f"182.{id_s}.1.0/24")

router_s_5a = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_5a.add_iface(iface, ip=f"182.{id_s}.0.2")
router_s_5a.add_iface(iface_s_5a, ip=f"182.{id_s}.1.1")
http_s_5a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_5a.add_iface(iface_s_5a, ip=f"182.{id_s}.1.2", gateway=f"182.{id_s}.1.1")

router_s_5b = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_5b.add_iface(iface, ip=f"182.{id_s}.0.3")
router_s_5b.add_iface(iface_s_5b, ip=f"182.{id_s}.1.1")
http_s_5b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_5b.add_iface(iface_s_5b, ip=f"182.{id_s}.1.2", gateway=f"182.{id_s}.1.1")

router_s_5c = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_5c.add_iface(iface, ip=f"182.{id_s}.0.4")
router_s_5c.add_iface(iface_s_5c, ip=f"182.{id_s}.1.1")
http_s_5c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_5c.add_iface(iface_s_5c, ip=f"182.{id_s}.1.2", gateway=f"182.{id_s}.1.1")

# ANYCAST SERVER 6 ************************************************************
# ANYCAST SERVER 7 ************************************************************
# ANYCAST SERVER 8 ************************************************************
# ANYCAST SERVER 9 ************************************************************

# SERVER GROUP 2 **************************************************************

id_sg = 2

iface_sg_2 = Iface(f"180.{id_sg}.0.0/16")
iface_sg = iface_sg_2

router_sg_2 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_sg_2.add_iface(iface_sg, ip=f"180.{id_sg}.0.1")
router_sg_2.add_iface(iface_br_b, ip=f"2.{id_br}.0.5")

# LB SERVER 10 ****************************************************************

id_s = 10

iface_s_10 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_10

router_s_10 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_10.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_10.add_iface(iface_sg, ip=f"180.{id_sg}.0.2")

lb_s_10 = LoadBalancer([f"182.{id_s}.0.3", f"182.{id_s}.0.4", f"182.{id_s}.0.5"], 
                       type=LBType.l4, algorithm=LBAlgorithm.leastconn, 
                       cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
lb_s_10.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")

http_s_10a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_10a.add_iface(iface, ip=f"182.{id_s}.0.3")
http_s_10b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_10b.add_iface(iface, ip=f"182.{id_s}.0.4")
http_s_10c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_10c.add_iface(iface, ip=f"182.{id_s}.0.5")

# LB SERVER 11 ****************************************************************

id_s = 11

iface_s_11 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_11

router_s_11 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_11.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_11.add_iface(iface_sg, ip=f"180.{id_sg}.0.3")

lb_s_11 = LoadBalancer([f"182.{id_s}.0.3", f"182.{id_s}.0.4", f"182.{id_s}.0.5"], 
                       type=LBType.l4, algorithm=LBAlgorithm.leastconn, 
                       cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
lb_s_11.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")

http_s_11a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_11a.add_iface(iface, ip=f"182.{id_s}.0.3")
http_s_11b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_11b.add_iface(iface, ip=f"182.{id_s}.0.4")
http_s_11c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_11c.add_iface(iface, ip=f"182.{id_s}.0.5")

# LB SERVER 12 ****************************************************************

id_s = 12

iface_s_12 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_12

router_s_12 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_12.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_12.add_iface(iface_sg, ip=f"180.{id_sg}.0.4")

lb_s_12 = LoadBalancer([f"182.{id_s}.0.3", f"182.{id_s}.0.4", f"182.{id_s}.0.5"], 
                       type=LBType.l4, algorithm=LBAlgorithm.random, 
                       cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
lb_s_12.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")

http_s_12a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_12a.add_iface(iface, ip=f"182.{id_s}.0.3")
http_s_12b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_12b.add_iface(iface, ip=f"182.{id_s}.0.4")
http_s_12c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_12c.add_iface(iface, ip=f"182.{id_s}.0.5")

# LB SERVER 13 ****************************************************************

id_s = 13

iface_s_13 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_13

router_s_13 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_13.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_13.add_iface(iface_sg, ip=f"180.{id_sg}.0.5")

lb_s_13 = LoadBalancer([f"182.{id_s}.0.3", f"182.{id_s}.0.4", f"182.{id_s}.0.5"], 
                       type=LBType.l4, algorithm=LBAlgorithm.random, 
                       cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
lb_s_13.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")

http_s_13a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_13a.add_iface(iface, ip=f"182.{id_s}.0.3")
http_s_13b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_13b.add_iface(iface, ip=f"182.{id_s}.0.4")
http_s_13c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_13c.add_iface(iface, ip=f"182.{id_s}.0.5")

# LB SERVER 14 ****************************************************************

id_s = 14

iface_s_14 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_14

router_s_14 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_14.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_14.add_iface(iface_sg, ip=f"180.{id_sg}.0.6")

lb_s_14 = LoadBalancer([f"182.{id_s}.0.3", f"182.{id_s}.0.4", f"182.{id_s}.0.5"], 
                       type=LBType.l4, algorithm=LBAlgorithm.roundrobin, 
                       cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
lb_s_14.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")

http_s_14a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_14a.add_iface(iface, ip=f"182.{id_s}.0.3")
http_s_14b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_14b.add_iface(iface, ip=f"182.{id_s}.0.4")
http_s_14c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_14c.add_iface(iface, ip=f"182.{id_s}.0.5")

# SERVER GROUP 3 **************************************************************

id_sg = 3

iface_sg_3 = Iface(f"180.{id_sg}.0.0/16")
iface_sg = iface_sg_3

router_sg_3 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_sg_3.add_iface(iface_sg, ip=f"180.{id_sg}.0.1")
router_sg_3.add_iface(iface_br_b, ip=f"2.{id_br}.0.6")

# LB SERVER 15 ****************************************************************

id_s = 15

iface_s_15 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_15

router_s_15 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_15.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_15.add_iface(iface_sg, ip=f"180.{id_sg}.0.2")

lb_s_15 = LoadBalancer([f"182.{id_s}.0.3", f"182.{id_s}.0.4", f"182.{id_s}.0.5"], 
                       type=LBType.l4, algorithm=LBAlgorithm.roundrobin, 
                       cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
lb_s_15.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")

http_s_15a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_15a.add_iface(iface, ip=f"182.{id_s}.0.3")
http_s_15b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_15b.add_iface(iface, ip=f"182.{id_s}.0.4")
http_s_15c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_15c.add_iface(iface, ip=f"182.{id_s}.0.5")

# LB SERVER 16 ****************************************************************

id_s = 16

iface_s_16 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_16

router_s_16 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_16.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_16.add_iface(iface_sg, ip=f"180.{id_sg}.0.3")

lb_s_16 = LoadBalancer([f"182.{id_s}.0.3", f"182.{id_s}.0.4", f"182.{id_s}.0.5"], 
                       type=LBType.l4, algorithm=LBAlgorithm.source, 
                       cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
lb_s_16.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")

http_s_16a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_16a.add_iface(iface, ip=f"182.{id_s}.0.3")
http_s_16b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_16b.add_iface(iface, ip=f"182.{id_s}.0.4")
http_s_16c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_16c.add_iface(iface, ip=f"182.{id_s}.0.5")

# LB SERVER 17 ****************************************************************

id_s = 17

iface_s_17 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_17

router_s_17 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_17.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_17.add_iface(iface_sg, ip=f"180.{id_sg}.0.4")

lb_s_17 = LoadBalancer([f"182.{id_s}.0.3", f"182.{id_s}.0.4", f"182.{id_s}.0.5"], 
                       type=LBType.l4, algorithm=LBAlgorithm.source, 
                       cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
lb_s_17.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")

http_s_17a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_17a.add_iface(iface, ip=f"182.{id_s}.0.3")
http_s_17b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_17b.add_iface(iface, ip=f"182.{id_s}.0.4")
http_s_17c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_17c.add_iface(iface, ip=f"182.{id_s}.0.5")

# LB SERVER 18 ****************************************************************

id_s = 18

iface_s_18 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_18

router_s_18 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_18.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_18.add_iface(iface_sg, ip=f"180.{id_sg}.0.5")

lb_s_18 = LoadBalancer([f"182.{id_s}.0.3", f"182.{id_s}.0.4", f"182.{id_s}.0.5"], 
                       type=LBType.l5, algorithm=LBAlgorithm.leastconn, 
                       cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
lb_s_18.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")

http_s_18a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_18a.add_iface(iface, ip=f"182.{id_s}.0.3")
http_s_18b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_18b.add_iface(iface, ip=f"182.{id_s}.0.4")
http_s_18c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_18c.add_iface(iface, ip=f"182.{id_s}.0.5")

# LB SERVER 19 ****************************************************************

id_s = 19

iface_s_19 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_19

router_s_19 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_19.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_19.add_iface(iface_sg, ip=f"180.{id_sg}.0.6")

lb_s_19 = LoadBalancer([f"182.{id_s}.0.3", f"182.{id_s}.0.4", f"182.{id_s}.0.5"], 
                       type=LBType.l5, algorithm=LBAlgorithm.leastconn, 
                       cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
lb_s_19.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")

http_s_19a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_19a.add_iface(iface, ip=f"182.{id_s}.0.3")
http_s_19b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_19b.add_iface(iface, ip=f"182.{id_s}.0.4")
http_s_19c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_19c.add_iface(iface, ip=f"182.{id_s}.0.5")

# SERVER GROUP 4 **************************************************************

id_sg = 4

iface_sg_4 = Iface(f"180.{id_sg}.0.0/16")
iface_sg = iface_sg_4

router_sg_4 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_sg_4.add_iface(iface_sg, ip=f"180.{id_sg}.0.1")
router_sg_4.add_iface(iface_br_b, ip=f"2.{id_br}.0.7")

# LB SERVER 20 ****************************************************************

id_s = 20

iface_s_20 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_20

router_s_20 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_20.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_20.add_iface(iface_sg, ip=f"180.{id_sg}.0.2")

lb_s_20 = LoadBalancer([f"182.{id_s}.0.3", f"182.{id_s}.0.4", f"182.{id_s}.0.5"], 
                       type=LBType.l5, algorithm=LBAlgorithm.random, 
                       cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
lb_s_20.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")

http_s_20a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_20a.add_iface(iface, ip=f"182.{id_s}.0.3")
http_s_20b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_20b.add_iface(iface, ip=f"182.{id_s}.0.4")
http_s_20c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_20c.add_iface(iface, ip=f"182.{id_s}.0.5")

# LB SERVER 21 ****************************************************************

id_s = 21

iface_s_21 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_21

router_s_21 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_21.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_21.add_iface(iface_sg, ip=f"180.{id_sg}.0.3")

lb_s_21 = LoadBalancer([f"182.{id_s}.0.3", f"182.{id_s}.0.4", f"182.{id_s}.0.5"], 
                       type=LBType.l5, algorithm=LBAlgorithm.random, 
                       cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
lb_s_21.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")

http_s_21a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_21a.add_iface(iface, ip=f"182.{id_s}.0.3")
http_s_21b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_21b.add_iface(iface, ip=f"182.{id_s}.0.4")
http_s_21c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_21c.add_iface(iface, ip=f"182.{id_s}.0.5")

# LB SERVER 22 ****************************************************************

id_s = 22

iface_s_22 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_22

router_s_22 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_22.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_22.add_iface(iface_sg, ip=f"180.{id_sg}.0.4")

lb_s_22 = LoadBalancer([f"182.{id_s}.0.3", f"182.{id_s}.0.4", f"182.{id_s}.0.5"], 
                       type=LBType.l5, algorithm=LBAlgorithm.roundrobin, 
                       cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
lb_s_22.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")

http_s_22a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_22a.add_iface(iface, ip=f"182.{id_s}.0.3")
http_s_22b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_22b.add_iface(iface, ip=f"182.{id_s}.0.4")
http_s_22c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_22c.add_iface(iface, ip=f"182.{id_s}.0.5")

# LB SERVER 23 ****************************************************************

id_s = 23

iface_s_23 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_23

router_s_23 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_23.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_23.add_iface(iface_sg, ip=f"180.{id_sg}.0.5")

lb_s_23 = LoadBalancer([f"182.{id_s}.0.3", f"182.{id_s}.0.4", f"182.{id_s}.0.5"], 
                       type=LBType.l5, algorithm=LBAlgorithm.roundrobin, 
                       cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
lb_s_23.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")

http_s_23a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_23a.add_iface(iface, ip=f"182.{id_s}.0.3")
http_s_23b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_23b.add_iface(iface, ip=f"182.{id_s}.0.4")
http_s_23c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_23c.add_iface(iface, ip=f"182.{id_s}.0.5")

# LB SERVER 24 ****************************************************************

id_s = 24

iface_s_24 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_24

router_s_24 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_24.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_24.add_iface(iface_sg, ip=f"180.{id_sg}.0.6")

lb_s_24 = LoadBalancer([f"182.{id_s}.0.3", f"182.{id_s}.0.4", f"182.{id_s}.0.5"], 
                       type=LBType.l5, algorithm=LBAlgorithm.source, 
                       cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
lb_s_24.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")

http_s_24a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_24a.add_iface(iface, ip=f"182.{id_s}.0.3")
http_s_24b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_24b.add_iface(iface, ip=f"182.{id_s}.0.4")
http_s_24c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_24c.add_iface(iface, ip=f"182.{id_s}.0.5")

# LB SERVER 25 ****************************************************************

id_s = 25

iface_s_25 = Iface(f"182.{id_s}.0.0/16")
iface = iface_s_25

router_s_25 = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
router_s_25.add_iface(iface, ip=f"182.{id_s}.0.1")
router_s_25.add_iface(iface_sg, ip=f"180.{id_sg}.0.7")

lb_s_25 = LoadBalancer([f"182.{id_s}.0.3", f"182.{id_s}.0.4", f"182.{id_s}.0.5"], 
                       type=LBType.l5, algorithm=LBAlgorithm.source, 
                       cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
lb_s_25.add_iface(iface, ip=f"182.{id_s}.0.2", gateway=f"182.{id_s}.0.1")

http_s_25a = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_25a.add_iface(iface, ip=f"182.{id_s}.0.3")
http_s_25b = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_25b.add_iface(iface, ip=f"182.{id_s}.0.4")
http_s_25c = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
http_s_25c.add_iface(iface, ip=f"182.{id_s}.0.5")


conf = Configurator()
