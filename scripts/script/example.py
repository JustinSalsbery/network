
from src.script import *
from time import sleep


def test_connectivity():
    run_command("client-0", "ping -c 5 100.0.0.1")
    run_command("client-0", "curl https://100.0.0.1/")


def create_tcpdump():
    run_background_command("client-0", "tcpdump -w shared/dump.pcap")

    test_connectivity()

    sleep(5)  # tcpdump is slow and requires time to process packets
    run_command("client-0", "pkill tcpdump")


if __name__ == "__main__":
    start_network("examples/server.py", 15)
    create_tcpdump()
    stop_network()
