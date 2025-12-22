
from src.components import *
from src.configurator import *


iface_0 = Iface()
iface_1 = Iface()

cidr_0 = "169.254.0.0/24"
cidr_1 = "169.254.0.0/24"

http_0 = HTTPServer(syn_cookie=SynCookieType.disable)
http_0.add_iface(iface_0, cidr=cidr_0, ip="169.254.0.1")
tgen_0 = TrafficGenerator(target="169.254.0.1", requests=["/40.html"], congestion_control=CongestionControlType.cubic)
tgen_0.add_iface(iface_0, cidr=cidr_0, ip="169.254.0.2", tc_rule=TCRule(drop=50))
tgen_1 = TrafficGenerator(target="169.254.0.1", requests=["/40.html"], congestion_control=CongestionControlType.reno)
tgen_1.add_iface(iface_0, cidr=cidr_0, ip="169.254.0.3", tc_rule=TCRule(drop=50))
client_0 = Client()
client_0.add_iface(iface_0, cidr=cidr_0, ip="169.254.0.4", tc_rule=TCRule(delay=100))

http_1 = HTTPServer(syn_cookie=SynCookieType.force)
http_1.add_iface(iface_1, cidr=cidr_1, ip="169.254.0.1")
tgen_2 = TrafficGenerator(target="169.254.0.1", requests=["/40.html"], congestion_control=CongestionControlType.cubic)
tgen_2.add_iface(iface_1, cidr=cidr_1, ip="169.254.0.2", tc_rule=TCRule(drop=50))
tgen_3 = TrafficGenerator(target="169.254.0.1", requests=["/40.html"], congestion_control=CongestionControlType.reno)
tgen_3.add_iface(iface_1, cidr=cidr_1, ip="169.254.0.3", tc_rule=TCRule(drop=50))
client_1 = Client()
client_1.add_iface(iface_1, cidr=cidr_1, ip="169.254.0.4", tc_rule=TCRule(delay=100))

Configurator()
