
from subprocess import getstatusoutput

def run_command(name: str, command: str) -> list[tuple[str, str, int]]:
    """
    @params:
        - name: The name of the container, ex. client-0, to run the command in.
                The name does not need to match exactly and will run for any container
                that contains the name.
        - command: The command to run. The command must exit and not wait. Uses `sh`.
    Returns: [(container name, output, status), ...]
    """

    _, o = getstatusoutput("docker container ls")

    containers = []
    for line in o.split("\n")[1:]:
        container = line.split(" ")[-1]
        containers.append(container)

    outputs = []
    for container in containers:
        if name not in container:
            continue

        s, o = getstatusoutput(f"docker exec {container} {command}")
        outputs.append((container, o, s))

    return outputs
