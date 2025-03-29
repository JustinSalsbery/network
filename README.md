
# Docker:
## Description:
- Simple deployment for various network configurations.

## Usage:
- Build docker images with `make build`.
- Tweak network configuration within `scripts/network/main.py`.
- Launch network with `make up`.
- Record container stats with `make stats`.
    - Network traffic can be recorded from the host machine with `tcpdump`.
- Shutdown network with `make down`.

## Notes:
- If the Makefile fails, update `make`. [Mac]
- Add the user to the `docker` group. [Linux]

## Useful `docker` commands:
- List:
    - List containers: `docker container ls -a`
    - List images: `docker image ls`
    - List networks: `docker network ls`
- Execute command: `docker exec <ID> <COMMAND>`
    - Execute interactive shell: `docker exec -it <ID> sh`
- Container lifecycle:
    - Start container: `docker start <ID>`
    - Stop container: `docker stop <ID>`
    - Kill container: `docker kill <ID>`
    - Restart container: `docker restart <ID>`
- Remove:
    - Remove container: `docker container rm <ID>`
    - Remove image: `docker image rm <IMAGE>`
    - Remove network: `docker network rm <ID>`
- Container information:
    - Container logs: `docker logs <ID>`
    - Inspect container: `docker inspect <ID>`
    - Resource usage: `docker stats`

## Misc:
- Access container ID w/in container: `$HOSTNAME`

---

# Todo:
## Containers: [Brainstorming]
- TOR: (1-step)
    - Client
    - Bridge
    - Node (Guard, Middle, Exit)
    - Directory Authority
    - Hidden Service
- General: (1-step)
    - Server:
        - Nginx
        - Apache
    - Traffic Generators:
        - `wrk`
        - Locust
        - Cricket
    - Load Balancers:
        - L4:
            - LVS IPVS
            - Katran
        - L5:
            - LVS KTCPVS
            - GitHub Load Balancer
            - Proxy (Nginx)
            - Proxy (HAProxy)
    - Network:
        - Router (SNAT w/ Firewall)
        - ECMP Router
        - BGP Router
        - Switch
    - Security:
        - IPS
        - IDS
    - Databases: [How would this interact with the server and traffic generator?]
        - Postgres
        - Redis
    - Miscellaneous:
        - Identifier: Utilizing ISN and Timestamp to fingerprint servers and identify the quantity of servers behind a load balancer.
        - Port scan (`nmap`)
        - IP scan (`nmap`)
        - Metasploitable2
- Kubernetes: (2-step)
    - Node            (1. Physical Setup)
    - Configurations: (2. YAML/Configurations)
        - Server
        - Load Balancers
        - Ingress
        - etc.
## Scripts:
- Randomly restart containers with the select image.
- Extend `network` to output `.gv` files, also known as Graphviz.
## Enhancements:
- Proper DNS Implementation
- Public and Private IP Addresses
    - Routers use a Firewall to block all private IP addresses
    - Routers can advertise many IPs (CIDR) on the public network
    - Services can use identifical IPs...

# ifconfig eth0 {IP} netmask 255.255.255.0
# route add default gateway {IP} eth0
