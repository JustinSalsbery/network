
from src.components import *
from src.configurator import *


# Creates COMPS_PER traffic generators within HOMES homes. 
# Creates SERVERS logical servers balancing between COMPS_PER backend servers.
# Each traffic generator within a home targets a logical server using the method
# specified in BALANCE_BY.
#
# The primary purpose of this script is to benchmark large network configurations.

# COMPONENT CONFIGURATION *****************************************************

PROTOCOL = Protocol.http
REQUESTS = ["/40.html"]
WAIT_MIN = 5
WAIT_MAX = 5
CONN_RATE = 20
CONN_MAX = 1000
CPU_LIMIT = 0.3
MEM_LIMIT = 256

# NETWORK CONFIGURATION *******************************************************

HOMES = 11
SERVERS = 11

# balance options are "NONE", "DNS", "ANYCAST", "LB-L{4, 5}-{random, roundrobin, source, leastconn}"
#                                               ex. "LB-L4-random" or "LB-L5-leastconn"
BALANCE_BY = ["NONE", "DNS", "ANYCAST", "LB-L4-random", "LB-L4-roundrobin", "LB-L4-source", \
              "LB-L4-leastconn", "LB-L5-random", "LB-L5-roundrobin", "LB-L5-source", \
              "LB-L5-leastconn"]

GROUP_BY = 4
COMPS_PER = 3

assert(HOMES % SERVERS == 0)  # assumed when assigning targets to traffic generators
assert(len(BALANCE_BY) == SERVERS)

# limited due to ip address space
assert(0 < HOMES <= 251 and 0 < SERVERS <= 253 and 0 < COMPS_PER <= 250)

# SELECT TARGETS **************************************************************

MULTIPLIER = HOMES // SERVERS

targets = []
for i in range(SERVERS):
    balance = BALANCE_BY[i]

    target = None
    if balance == "DNS":
        target = f"dns-server-{i}"
    elif balance == "ANYCAST":
        target = f"182.{i}.1.2"
    elif balance == "NONE":
        target = f"182.{i}.0.2"
    elif "LB" in balance:
        target = f"182.{i}.0.2"
    else:
        print(f"Unknown balance method: {balance}")
        exit(1)

    for _ in range(MULTIPLIER):
        targets.append(target)


# HOMES ***********************************************************************

iface_backbone = Iface("1.0.0.0/8")  # setup dns root

dns_root = DNSServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
dns_root.add_iface(iface_backbone, ip="1.255.255.254", gateway="1.0.0.1")
DNS_ROOT = ["1.255.255.254"]

for _ in range(1):  # setup backbone routers
    iface_backbone_ext = Iface("2.0.0.0/16")

    router = Router(ecmp=ECMPType.l3, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
    router.add_iface(iface_backbone, ip="1.0.0.1")
    router.add_iface(iface_backbone_ext, ip="2.0.0.1")

    router = Router(ecmp=ECMPType.l3, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
    router.add_iface(iface_backbone, ip="1.0.0.2")
    router.add_iface(iface_backbone_ext, ip="2.0.0.2")

    # homes are grouped together
    groups = HOMES // GROUP_BY + 1
    if HOMES % GROUP_BY == 0:
        groups = HOMES // GROUP_BY

    for i in range(groups):  # setup home groups
        iface_group = Iface(f"170.{i}.0.0/16")

        router = Router(ecmp=ECMPType.l4, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
        router.add_iface(iface_backbone_ext, ip=f"2.0.0.{i + 3}")
        router.add_iface(iface_group, ip=f"170.{i}.0.1")

        for j in range(GROUP_BY):  # setup homes within group
            home = i * GROUP_BY + j  # the home number (irrespective of the loop)
            if home >= HOMES:
                break

            iface = Iface("172.16.0.0/12")

            router = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
            router.add_iface(iface_group, ip=f"170.{i}.0.{j + 2}")
            router.add_iface(iface, nat=NatType.snat_input, ip="172.16.0.1")

            server = home // MULTIPLIER
            balance = BALANCE_BY[server]

            if balance == "DNS":  # creates dns server only if needed
                dns = DNSServer(dns_servers=DNS_ROOT, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
                dns.add_iface(iface, ip="172.16.0.2", gateway="172.16.0.1")

            target = targets[home]
            for n in range(COMPS_PER):
                tgen = TrafficGenerator(target=target, proto=PROTOCOL, requests=REQUESTS,
                                        conn_max=CONN_MAX, conn_rate=CONN_RATE, 
                                        wait_min=WAIT_MIN, wait_max=WAIT_MAX, 
                                        dns_server="172.16.0.2",  # dns server may not exist
                                        cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
                tgen.add_iface(iface, ip=f"172.16.0.{n + 3}", gateway="172.16.0.1")

# SERVERS *********************************************************************

for _ in range(1):  # setup backbone routers
    iface_backbone_ext = Iface("2.1.0.0/16")

    router = Router(ecmp=ECMPType.l3, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
    router.add_iface(iface_backbone, ip="1.0.0.3")
    router.add_iface(iface_backbone_ext, ip="2.1.0.1")

    router = Router(ecmp=ECMPType.l3, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
    router.add_iface(iface_backbone, ip="1.0.0.4")
    router.add_iface(iface_backbone_ext, ip="2.1.0.2")

    # servers are grouped together
    groups = HOMES // GROUP_BY + 1
    if HOMES % GROUP_BY == 0:
        groups = HOMES // GROUP_BY

    for i in range(groups):  # setup server groups
        iface_group = Iface(f"180.{i}.0.0/16")

        router = Router(ecmp=ECMPType.l4, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
        router.add_iface(iface_backbone_ext, ip=f"2.1.0.{i + 3}")
        router.add_iface(iface_group, ip=f"180.{i}.0.1")

        for j in range(GROUP_BY):  # setup server within group
            server = i * GROUP_BY + j  # the server number (irrespective of the loop)
            if server >= SERVERS:
                break

            iface = Iface(f"182.{server}.0.0/16")

            router = Router(ecmp=ECMPType.l4, cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
            router.add_iface(iface_group, ip=f"180.{i}.0.{j + 2}")
            router.add_iface(iface, ip=f"182.{server}.0.1")

            # the topography of the server is dependent on the balancing strategy
            balance = BALANCE_BY[server]

            assert(type(balance) is str)
            if "LB" in balance:  # the load balancer is shared
                if "L4" in balance:
                    lb_type = LBType.l4
                elif "L5" in balance:
                    lb_type = LBType.l5
                else:
                    print(f"Unknown layer: {balance}")
                    exit(1)

                if "random" in balance:
                    algorithm = LBAlgorithm.random
                elif "roundrobin" in balance:
                    algorithm = LBAlgorithm.roundrobin
                elif "source" in balance:
                    algorithm = LBAlgorithm.source
                elif "leastconn" in balance:
                    algorithm = LBAlgorithm.leastconn
                else:
                    print(f"Unknown algorithm: {balance}")
                    exit(1)

                servers = []  # the IP addresses of the backend servers
                for n in range(COMPS_PER):
                    servers.append(f"182.{server}.0.{n + 3}")

                lb = LoadBalancer(servers, type=lb_type, algorithm=algorithm,
                                  cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
                lb.add_iface(iface, ip=f"182.{server}.0.2", gateway=f"182.{server}.0.1")
                
            for n in range(COMPS_PER):
                if balance == "DNS":  # creates a server and DNS entry
                    http = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
                    http.add_iface(iface, ip=f"182.{server}.0.{n + 2}", gateway=f"182.{server}.0.1")
                    dns_root.register(f"dns-server-{server}", f"182.{server}.0.{n + 2}")
                
                elif balance == "ANYCAST":  # creates a router and a server
                    iface_int = Iface(f"182.{server}.1.0/24")

                    router = Router(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
                    router.add_iface(iface, ip=f"182.{server}.0.{n + 2}")
                    router.add_iface(iface_int, ip=f"182.{server}.1.1")
                    http = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
                    http.add_iface(iface_int, ip=f"182.{server}.1.2", 
                                   gateway=f"182.{server}.1.1")
                    
                elif balance == "NONE":  # creates exactly 1 server, regardless of COMPS_PER
                    http = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
                    http.add_iface(iface, ip=f"182.{server}.0.2", gateway=f"182.{server}.0.1")
                    break

                elif "LB" in balance:  # creates a server; the load balancer is created above
                    http = HTTPServer(cpu_limit=CPU_LIMIT, mem_limit=MEM_LIMIT)
                    http.add_iface(iface, ip=f"182.{server}.0.{n + 3}")

                else:
                    print(f"Unknown balance method: {balance}")
                    exit(1)


conf = Configurator()
