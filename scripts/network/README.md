
# Config:
## Description:
- Writes a `docker compose` file based on the configuration within the python file.
- Enables easy creation and deployment of various network configurations.

## References
- Useful commands are written within the corresponding `component/startup.sh`, for example:
    - Example `tor` usage with the `$TOR_CURL` variable.
    - Example `bird` commands for routing information.

## Supported components:
- Client
- TrafficGenerator
- HTTPServer
- DHCPServer
- DNSServer
- LoadBalancer
- TorNode
- Router

## Usage:
- `python3 main.py`
