#!/bin/sh

interfaces=$(ls /sys/class/net)

for interface in $interfaces; do
    ips=$(ip address show $interface | awk '/inet / {print $2}' | cut -d'/' -f1)

    for ip in $ips; do
        if [ "$ip" = "$SOURCE_IP" ]; then
            ip route add default via $GATEWAY dev $interface
        fi
    done
done

top

# CMD ["venv/bin/python3", "main.py"]
