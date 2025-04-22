
# Docker:
## Description:
- Simple deployment for various network configurations.

## Usage:
- Build docker images with `make build`.
- Tweak network configuration within `scripts/network/main.py`.
- Launch network with `make up`.
- Record container stats with `make stats`.
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
1. NTP: Add WARNING to Tor.
    - Docker uses the host clock so NTP is unnecessary for clock synchronization.
    - Many encrypted protocols require clock synchronization, such as HTTPS and Tor,
      so NTP may be necessary in a real-world environment.
2. Server: Static and dynamic pages.

Neat additions:
- Damn Vulnerable Web App
- nmap: Port and IP scanners
- IDS: Router option to duplicate traffic to IDS.
- VPN: Router options for IP destination censorship and port forwarding.

Needed scripts:
- Generate graph by connecting components to their interface. Use IPs as the edge labels and the container names as the node name.
- Randomly restart containers with a select image name.
