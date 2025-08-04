
# Docker:
## Description:
- Simple deployment for various network configurations.

## Requirements:
- Linux: [Supported on Debian-based Distributions]
    - Add the user to the `docker` group.
- Mac: [Unsupported]
    - Use a recent version of `make`.
    - Currently, neither `dhcp` nor the `routers` will function correctly.
- Windows: [Untested]

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
        - The container is shutdown. Ongoing connections are cleanly closed.
    - Restart container: `docker restart <ID>`
- Remove:
    - Remove container: `docker container rm <ID>`
    - Remove image: `docker image rm <IMAGE>`
    - Remove network: `docker network rm <ID>`
- Container information:
    - Container logs: `docker logs <ID>`
        - Only STDOUT: `docker logs <ID> 2> /dev/null`
        - Only STDERR: `docker logs <ID> 1> /dev/null`
    - Inspect container: `docker inspect <ID>`
    - Resource usage: `docker stats`

## Misc:
- Access the container ID within the container with `$HOSTNAME`.
