
from network import *

create_network("internal", "169.254.0.0/16", "169.254.0.1")
create_server("nginx", "internal", "169.254.0.2")
create_traffic_generator("locust-1", "internal", "169.254.0.3", "169.254.0.2", max_connections=800, pages="40.html", disable_swap=True)
create_traffic_generator("locust-2", "internal", "169.254.0.4", "169.254.0.2", max_connections=800, pages="40.html", disable_swap=True)
create_traffic_generator("locust-3", "internal", "169.254.0.5", "169.254.0.2", max_connections=800, pages="40.html", disable_swap=True)

write_conf()
