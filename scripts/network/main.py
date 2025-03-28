
from network import *

create_network("a", "169.254.0.0/24", "169.254.0.1")
create_server("nginx", "a", "169.254.0.2")

create_network("b", "169.254.1.0/24", "169.254.1.1")
create_traffic_generator("locust", "b", "169.254.1.2", "169.254.0.2", max_connections=800, pages="40.html", disable_swap=True)

write_conf()
