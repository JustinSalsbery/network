
import psutil

from sys import argv
from io import TextIOWrapper
from time import sleep, time


def measure(wait: float, iface: str, path: str):
    with open(path, "w") as file:
        file.write("timestamp,")

        cpu = psutil.cpu_count(logical=True)
        for core in range(cpu):
            file.write(f"cpu{core}_percent," +  # cpu{core}_frequency,
                       f"cpu{core}_user_time,cpu{core}_system_time,cpu{core}_idle_time,")

        file.write("ctx_switches,interrupts,syscalls,mem_percent,mem_total,mem_available," +
                   "mem_used,mem_cache_bytes,net_sent_bytes,net_received_bytes," +
                   "net_packets_sent,net_packets_received,sock_established,sock_closing," +
                   "disk_reads_count,disk_writes_count,disk_read_bytes,disk_write_bytes\n")

        while True:
            __measure(file, cpu, iface)
            sleep(wait)


def __measure(file: TextIOWrapper, cpu: int, iface: str):
    file.write(f"{time():1f},")  # timestamp

    cpu_percents = psutil.cpu_percent(interval=None, percpu=True)
    # cpu_frequencies = psutil.cpu_freq(percpu=True) # empty list
    cpu_times = psutil.cpu_times(percpu=True)

    for core in range(cpu):
        file.write(f"{cpu_percents[core]}," +  # {cpu_frequencies[core]},
                   f"{cpu_times[core].user},{cpu_times[core].system},{cpu_times[core].idle},")

    cpu_stats = psutil.cpu_stats()

    v_mem = psutil.virtual_memory()

    net_io = \
        psutil.net_io_counters(pernic=True, nowrap=True)[iface]
    net_connections = psutil.net_connections(kind="tcp")

    established = 0
    closing = 0

    for connection in net_connections:
        established += 1 if connection[5] == "ESTABLISHED" else 0
        closing += 1 if connection[5] == "TIME_WAIT" else 0

    disk_io = psutil.disk_io_counters(perdisk=False, nowrap=True)

    file.write(
        f"{cpu_stats.ctx_switches},{cpu_stats.interrupts},{cpu_stats.syscalls}," +
        f"{v_mem.percent},{v_mem.total},{v_mem.available},{v_mem.total - v_mem.available}," +
        f"{v_mem.cached},{net_io.bytes_sent},{net_io.bytes_recv},{net_io.packets_sent}," +
        f"{net_io.packets_recv},{established},{closing},{disk_io.read_count}," +
        f"{disk_io.write_count},{disk_io.read_bytes},{disk_io.write_bytes}\n")


if __name__ == "__main__":
    if len(argv) != 4:
        print(f"usage: {argv[0]} precision interface output")
        exit(1)

    wait = argv[1] / 1000
    iface = argv[2]
    path = argv[3]

    measure(wait, iface, path)
