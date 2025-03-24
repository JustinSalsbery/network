
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
## Containers:
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
        - LVS IPVS
        - LVS KTCPVS
        - Katran
        - GitHub Load Balancer
        - Proxy (Nginx)
    - Network:
        - Router
        - ECMP Router
        - BGP Router
        - Switch
    - Miscellaneous:
        - Identifier: Utilizing ISN and Timestamp to fingerprint servers and identify the quantity of servers behind a load balancer.
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
- Move away from using `dicts` to using `structs`.
- Make container (1) naming optional and (2) specifying IP optional.
    - Randomly generate the above if not provided.
- Support containers using multiple networks.
- Explore how network gateways work.
    - Containers should be able to route between different networks.
    - This may require specifying routes within the container.
