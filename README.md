
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
    - I no longer support Mac. The networking is not working correctly!
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
Needed for work:
1. HAproxy
2. Katran
3. Tor
4. CDN
5. K8s

Needed foundation:
1. NTP
2. DNS
3. DHCP

Neat additions:
- Metasploitable 2
- nmap (Port and IP scanners)
- VPN
    - Local only firewall rule.
    - IP destination censorship on routers

Eventual:
- Server:
    - Redis for authentication.
    - Postgres for storage.
    - API access
- Script: `pcap` to `dot` graph
- Script: Randomly restart containers with image name.

Avoid for simplicity:
- CA
    - Copy certificates into containers so `--insecure` flag isn’t required?
- Autonomous zones.
- IPS
    - Difficult to input rules.
