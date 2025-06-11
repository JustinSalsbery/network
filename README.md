
# Docker:
## Description:
- Simple deployment for various network configurations.

## Requirements:
- Linux: [Supported on Debian-based Distributions]
    - Add the user to the `docker` group.
    - While not necessary, the following file should exist: `/boot/config-$(uname -r)`
- Mac: [Unsupported]
    - Use a recent version of `make`.
    - Currently, neither `dhcp` nor the `routers` will function correctly.
- Windows: [Unsupported and Untested]

## Usage:
- Build docker images with `make build`.
- Tweak network configuration within `scripts/network/main.py`.
- Launch network with `make up`.
- Record container stats with `make stats`.
- Record network traffic from the host with `tcpdump`. You must specify the interface!
    - Note that Wireshark is not designed for a global network view and labels any packet that has a duplicate 5-tuple as being a retransmissions. All forwarded packets, such as by a router, will be labeled as a retransmission regardless of originating from a different MAC address.
- Shutdown network with `make down`.

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
        - STDOUT: `docker logs <ID> 2> /dev/null`
        - STDERR: `docker logs <ID> 1> /dev/null`
    - Inspect container: `docker inspect <ID>`
    - Resource usage: `docker stats`

## Misc:
- Access the container ID within the container with `$HOSTNAME`.

---

# Todo:
0. Rework `tc` particularly rate; and add MTU to iface_add
1. Rework Logging
    - Logging should be enabled by default to STDERR
    - Remove Logging Toggles
2. CDN for Caching
    - I could cache on the L5 LB instead.
    - Vary HTTP Header: Enable or Disable Caching
    - Max-age HTTP Header: TTL for Caching
3. K8s Deployments
4. Random restart script

---

# Considered:
I want to limit the scope so that future maintanence is easier. I have considered adding many new components, including the following:

1. Tor
2. VPN
3. IDS
4. ... and many more.

I may consider adding such components in the future if I see a need.
