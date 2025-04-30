
# silence scapy startup warnings
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)  # nopep8

from sys import argv
from scapy.all import PcapReader, Ether, IP, TCP
from scapy.layers.http import HTTPRequest, HTTPResponse


def main():
    start, end = 0, 0  # by unit of precision; 0 unbounded
    precision = 0  # ms
    input = ""  # to pcap
    output = ""  # csv

    if len(argv) == 4:
        precision = int(argv[1])
        input = argv[2]
        output = argv[3]
    elif len(argv) == 6:
        start = int(argv[1])
        end = int(argv[2])
        precision = int(argv[3])
        input = argv[4]
        output = argv[5]
    else:
        print("Options:")
        print(f"\t- python {argv[0]} precision input output")
        print(f"\t- python {argv[0]} start end precision input output")
        exit(1)

    unit = precision / 1_000
    shift = 1_000 / precision

    pcap = PcapReader(input)
    flags, end = read(pcap, start, end, shift)

    write(output, flags, start, end, unit)


def read(pcap: PcapReader, start: int, end: int, shift: float) -> tuple[dict, int]:
    flags = {}
    table = {}

    packet = pcap.read_packet()
    offset = int(packet.time * shift)

    if start == 0:  # .read_packet() removes packet from pcap
        add_packet(flags, table, packet, 0)

    time = 0
    for packet in pcap:
        time = int(packet.time * shift) - offset
        if end != 0 and end < time:
            break

        if start <= time:
            add_packet(flags, table, packet, time)

    if end != 0 and end < time:
        return (flags, end)  # time is 1 index off
    return (flags, time)


def add_packet(flags: dict, table: dict, packet: Ether, time: int) -> None:
    if TCP not in packet:
        return

    if time not in flags:
        flags[time] = {"Total": 0, "SYN": 0, "SYN/ACK": 0, "ACK and PSH/ACK": 0, "ACK": 0, "PSH/ACK": 0,
                       "0-Length ACK": 0, "0-Window ACK": 0, "HTTP Request": 0, "Total HTTP Request Size": 0,
                       "Retransmitted HTTP Request": 0, "Total Retransmitted HTTP Request Size": 0,
                       "HTTP Response": 0, "Total HTTP Response Size": 0, "Retransmitted HTTP Response": 0,
                       "Total Retransmitted HTTP Response Size": 0, "FIN": 0, "FIN/ACK": 0, "RST": 0}

    flags[time]["Total"] += 1

    if packet[TCP].flags == "S":
        flags[time]["SYN"] += 1
    elif packet[TCP].flags == "SA":
        flags[time]["SYN/ACK"] += 1
    elif packet[TCP].flags == "A" or packet[TCP].flags == "PA":
        flags[time]["ACK and PSH/ACK"] += 1
        if packet[TCP].flags == "A":
            flags[time]["ACK"] += 1
        elif packet[TCP].flags == "PA":
            flags[time]["PSH/ACK"] += 1

        if packet[TCP].window == 0:
            flags[time]["0-Window ACK"] += 1
        elif length(packet) == 0:
            flags[time]["0-Length ACK"] += 1

        hash = (packet[IP].src, packet[IP].dst,
                packet[TCP].sport, packet[TCP].dport)
        position = (packet[TCP].seq, packet[TCP].ack)

        if HTTPRequest in packet:
            flags[time]["HTTP Request"] += 1
            flags[time]["Total HTTP Request Size"] += length(packet)

            if hash not in table:
                table[hash] = []

            if position in table[hash]:
                flags[time]["Retransmitted HTTP Request"] += 1
                flags[time]["Total Retransmitted HTTP Request Size"] += \
                    length(packet)
            else:
                table[hash].append(position)

        elif HTTPResponse in packet:
            flags[time]["HTTP Response"] += 1
            flags[time]["Total HTTP Response Size"] += length(packet)

            if hash not in table:
                table[hash] = []

            if position in table[hash]:
                flags[time]["Retransmitted HTTP Response"] += 1
                flags[time]["Total Retransmitted HTTP Response Size"] += \
                    length(packet)
            else:
                table[hash].append(position)

    elif packet[TCP].flags == "F":
        flags[time]["FIN"] += 1
    elif packet[TCP].flags == "FA":
        flags[time]["FIN/ACK"] += 1
    elif packet[TCP].flags == "R":
        flags[time]["RST"] += 1


# len(packet[TCP].payload) return unencoded length
def length(packet: Ether) -> int:
    ip_length = packet[IP].len
    ip_header_length = packet[IP].ihl * 4
    tcp_header_length = packet[TCP].dataofs * 4
    return ip_length - ip_header_length - tcp_header_length


def write(output: str, flags: dict, start: int, end: int, unit: int):
    with open(output, "w") as file:
        file.write("Time (s),Total,SYN,SYN/ACK,ACK and PSH/ACK,ACK, PSH/ACK,"
                   + "0-Length ACK,0-Window ACK,HTTP Request,Total HTTP Request Size,"
                   + "Average HTTP Request Size,Retransmitted HTTP Request,"
                   + "Total Retransmitted HTTP Request Size,Average Retransmitted HTTP Request Size,"
                   + "HTTP Response,Total HTTP Response Size,Average HTTP Response Size,"
                   + "Retransmitted HTTP Response,Total Retransmitted HTTP Response Size,"
                   + "Average Retransmitted HTTP Response Size,FIN,FIN/ACK,RST,"
                   + "Estimated Number of Connections\n")

        estimated_connections = 0
        for i in range(start, end + 1):
            if i not in flags:
                file.write(f"{i * unit:.3f},0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,"
                           + "0,0,0,0\n")
            else:
                stats = flags[i]

                # For estimating # of connections:
                #   SYN and SYN/ACK open in 1-direction
                #   FIN and FIN/ACK close in 1-direction
                #   RST closes in both directions

                # Unaccounted for errors:
                #   Retransmitted SYN, SYN/ACK, FIN, FIN/ACK, RST
                #   RST in response to SYN, FIN, or FIN/ACK
                
                estimated_connections += (stats["SYN"] + stats["SYN/ACK"]) \
                    - (stats["FIN"] + stats["FIN/ACK"] + 2 * stats["RST"])

                avg_request_size = 0 if stats["HTTP Request"] == 0 \
                    else stats["Total HTTP Request Size"] // stats["HTTP Request"]
                avg_response_size = 0 if stats["HTTP Response"] == 0 \
                    else stats["Total HTTP Response Size"] // stats["HTTP Response"]

                avg_retrans_request_size = 0 if stats["Retransmitted HTTP Request"] == 0 \
                    else stats["Total Retransmitted HTTP Request Size"] // stats["Retransmitted HTTP Request"]
                avg_retrans_response_size = 0 if stats["Retransmitted HTTP Response"] == 0 \
                    else stats["Total Retransmitted HTTP Response Size"] // stats["Retransmitted HTTP Response"]

                file.write(f"{i * unit:.3f},{stats["Total"]},{stats["SYN"]},{stats["SYN/ACK"]},"
                           + f"{stats["ACK and PSH/ACK"]},{stats["ACK"]},{stats["PSH/ACK"]},"
                           + f"{stats["0-Length ACK"]},{stats["0-Window ACK"]},"
                           + f"{stats["HTTP Request"]},{stats["Total HTTP Request Size"]},"
                           + f"{avg_request_size},{stats["Retransmitted HTTP Request"]},"
                           + f"{stats["Total Retransmitted HTTP Request Size"]},"
                           + f"{avg_retrans_request_size},{stats["HTTP Response"]},"
                           + f"{stats["Total HTTP Response Size"]},{avg_response_size},"
                           + f"{stats["Retransmitted HTTP Response"]},"
                           + f"{stats["Total Retransmitted HTTP Response Size"]},"
                           + f"{avg_retrans_response_size},{stats["FIN"]},{stats["FIN/ACK"]},"
                           + f"{stats["RST"]},{estimated_connections / 2:.1f}\n")


if __name__ == "__main__":
    main()
