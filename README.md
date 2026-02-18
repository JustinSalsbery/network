
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
- For help, type `make`.
- Build docker images with `make build`.
    - This must be done before launching a network!
- Launch a network with `make up`.
    - `make up` will launch the default network located at `scripts/network/main.py`.
    - To launch a specific network, use `make up NETWORK=<NAME>`.
        - To view all networks, use `make list-networks`.
- Record container stats with `make stats`.
- Record network traffic from a container or the host with `tcpdump`. You must specify the interface!
    - Note that Wireshark is not designed for a global network view and labels any packet that has a duplicate 5-tuple as being a retransmissions. All forwarded packets, such as by a router, will be labeled as a retransmission regardless of originating from a different MAC address.
- Shutdown network with `make down`.

## Useful `docker` commands:
- List:
    - List containers: `docker container ls -a`
    - List images: `docker image ls`
    - List networks: `docker network ls`
- Execute command: `docker exec <NAME> <COMMAND>`
    - Execute interactive shell: `docker exec -it <NAME> sh`
- Container lifecycle:
    - Start container: `docker start <NAME>`
    - Stop container: `docker stop <NAME>`
    - Kill container: `docker kill <NAME>`
        - The container is shutdown. Ongoing connections are cleanly closed.
    - Restart container: `docker restart <NAME>`
- Remove:
    - Remove container: `docker container rm <NAME>`
    - Remove image: `docker image rm <IMAGE>`
    - Remove network: `docker network rm <NAME>`
- Container information:
    - Container logs: `docker logs <NAME>`
        - Only STDOUT: `docker logs <NAME> 2> /dev/null`
        - Only STDERR: `docker logs <NAME> 1> /dev/null`
    - Inspect container: `docker inspect <NAME>`
    - Resource usage: `docker stats`

## Misc:
- Access the container NAME within the container with `$HOSTNAME`.
