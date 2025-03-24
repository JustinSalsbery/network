
from signal import signal, SIGINT
from subprocess import getstatusoutput
from time import time, sleep


OUTPUT = "shared"
CONTAINERS = {} # container_id: [stats]
WAIT = 5


def to_bytes(value: str) -> str:
    if value.endswith("GiB"):
        return f"{int(float(value[:-3]) * 1_073_742_000)}"
    elif value.endswith("MiB"):
        return f"{int(float(value[:-3]) * 1_048_576)}"
    elif value.endswith("KiB"):
        return f"{int(float(value[:-3]) * 1_024)}"
    elif value.endswith("GB"):
        return f"{int(float(value[:-2]) * 1_000_000_000)}"
    elif value.endswith("MB"):
        return f"{int(float(value[:-2]) * 1_000_000)}"
    elif value.endswith("kB"):
        return f"{int(float(value[:-2]) * 1_000)}"
    elif value.endswith("B"):
        return f"{int(value[:-1])}"
    else: # likely will match above and crash
        return value


def monitor_stats():
    while True:
        s, o = getstatusoutput("docker stats --no-stream | tr -s ' '")
        if s != 0:
            print(o)
            exit(s)

        o = o.splitlines()
        if len(o) < 2:
            sleep(WAIT)
            continue

        for line in o[1:]:
            line = line.split()

            container_id = line[0]
            container_name = line[1]
            cpu_perc = line[2]
            mem_usage = to_bytes(line[3])
            mem_limit = to_bytes(line[5])
            mem_perc = line[6]
            net_received = to_bytes(line[7])
            net_transmitted = to_bytes(line[9])
            disk_read = to_bytes(line[10])
            disk_write = to_bytes(line[12])
            pids = line[13]

            if container_id not in CONTAINERS:
                CONTAINERS[container_id] = []

            CONTAINERS[container_id].append(f"{time():1f},{container_id},{container_name},"
                                            + f"{cpu_perc},{mem_usage},{mem_limit},{mem_perc},"
                                            + f"{net_received},{net_transmitted},"
                                            + f"{disk_read},{disk_write},{pids}\n")
            
        sleep(WAIT)


def write_stats():
    header = "timestamp,container_id,container_name,cpu_perc,mem_usage,mem_limit,mem_perc," \
             + "net_received,net_transmitted,disk_read,disk_write,pids\n"
    
    for container_id, stats in CONTAINERS.items():
        with open(f"{OUTPUT}/stats-{container_id}.csv", "w") as file:
            file.write(header)
            
            for stat in stats:
                file.write(stat)


def signal_handler(sig, frame):
    write_stats()
    exit(0)


if __name__ == "__main__":
    signal(SIGINT, signal_handler)
    monitor_stats()
