
from subprocess import getstatusoutput, Popen
from time import sleep


def run_command(
        name: str,
        command: str,
        exit_on_failure: bool = True,
    ) -> list[tuple[str, str, int]]:

    """
    @params:
        - name: The name of the container, ex. client-0, to run the command in.
                The name does not need to match exactly and will run for any container
                that contains the name.
        - command: The command to run. The command must exit and not wait. Uses `sh`.
    Returns: [(container name, status, output), ...]
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

        print(f"running '{command}' on {container}")

        s, o = getstatusoutput(f"docker exec {container} {command}")
        if exit_on_failure and s != 0:
            print(f"{container} failed with status {s}:\ncommand: {command}\noutput: {o}")
            exit(1)

        outputs.append((container, s, o))
    return outputs


def run_background_command(name: str, command: str):
    """
    @params:
        - name: The name of the container, ex. client-0, to run the command in.
                The name does not need to match exactly and will run for any container
                that contains the name.
        - command: The command to run. The command will run in the background. Uses `sh`.
                   Do not use &.
    """

    _, o = getstatusoutput("docker container ls")

    containers = []
    for line in o.split("\n")[1:]:
        container = line.split(" ")[-1]
        containers.append(container)

    for container in containers:
        if name not in container:
            continue

        print(f"running '{command}' in the background on {container}")

        docker_command = f"docker exec {container} {command}"
        Popen(docker_command.split(" "))


def start_network(config: str, wait_for: int = 30):
    """
    @params:
        - config: The network configuration to start. ex. 'examples/server.py'
        - wait_for: The time to wait for the network to initialize. In seconds.
    """

    print(f"starting network with config '{config}'")
    s, o = getstatusoutput(f"make up CONFIG={config}")

    if s != 0:
        print(f"failed with status {s}: {o}")
        exit(1)

    print(f"waiting for {wait_for} seconds for the network to initialize")
    sleep(wait_for)


def stop_network():
    print("stopping network")
    s, o = getstatusoutput("make down")

    if s != 0:
        print(f"failed with status {s}: {o}")
        exit(1)
