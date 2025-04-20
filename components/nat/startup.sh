#!/bin/sh

# delete docker configurations
echo "localhost 127.0.0.1" > /etc/hosts
echo "" > /etc/resolv.conf

# disable ipv6
sysctl -w net.ipv6.conf.all.disable_ipv6=1

# setup ifaces
for IFACE in $IFACES; do
    IP="$(echo $IPS | cut -d' ' -f1)"    # the first index
    IPS="$(echo $IPS | cut -d' ' -f2-)"  # the rest of the list

    NET_MASK="$(echo $NET_MASKS | cut -d' ' -f1)"
    NET_MASKS="$(echo $NET_MASKS | cut -d' ' -f2-)"

    GATEWAY="$(echo $GATEWAYS | cut -d' ' -f1)"
    GATEWAYS="$(echo $GATEWAYS | cut -d' ' -f2-)"

    # network suffix should be _0
    if [ "$IP" = "none" ]; then
        # dhcp
        umount /etc/resolv.conf  # docker mounts resolv.conf
        udhcpc -i ${IFACE}_0     # unmounting allows dhcp to write resolv.conf
    else
        # manual
        ifconfig ${IFACE}_0 $IP netmask $NET_MASK

        if [ "$GATEWAY" != "none" ]; then
            route add default gateway $GATEWAY ${IFACE}_0
        fi

        if [ "$NAMESERVER" != "none" ]; then
            echo "nameserver $NAMESERVER" > /etc/resolv.conf
        fi
    fi
done

# setup forwarding
if [ "$FORWARD" = "true" ]; then
    sysctl -w net.ipv4.ip_forward=1
else
    sysctl -w net.ipv4.ip_forward=0
fi

# setup firewall
for IFACE in $IFACES; do
    FIREWALL="$(echo $FIREWALLS | cut -d' ' -f1)"
    FIREWALLS="$(echo $FIREWALLS | cut -d' ' -f2-)"

    # for routers, add rules to forwarding table

    # routing protocols, vpns, k8s, databases, etc are unaccounted for
    # limit ports:
    #   - tcp: 22 (ssh), 80 (http), 443 (https), 5000 (tor node), 7000 (tor directory), 9050 (tor socks)
    #   - udp: 53 (dns), 67 (dhcp), 123 (ntp), 443 (quic)

    # block new incoming connections; internal endpoints must initiate all connections
    if [ "$FIREWALL" = "block_new_conn_input" ]; then
        iptables -A FORWARD -o ${IFACE}_0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
        iptables -A FORWARD -o ${IFACE}_0 -j DROP

    # block new incoming connections and limit ports
    elif [ "$FIREWALL" = "block_new_conn_input_strict" ]; then
        iptables -A FORWARD -i ${IFACE}_0 -p tcp -m multiport --dports 22,80,443,5000,7000,9050 -j ACCEPT
        iptables -A FORWARD -i ${IFACE}_0 -p tcp -j DROP

        iptables -A FORWARD -i ${IFACE}_0 -p udp -m multiport --dports 53,123,443 -j ACCEPT
        iptables -A FORWARD -i ${IFACE}_0 -p udp -j DROP

        iptables -A FORWARD -o ${IFACE}_0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
        iptables -A FORWARD -o ${IFACE}_0 -j DROP

    # block new outgoing connections; external endpoints must initiate all connections
    elif [ "$FIREWALL" = "block_new_conn_output" ]; then
        iptables -A FORWARD -i ${IFACE}_0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
        iptables -A FORWARD -i ${IFACE}_0 -j DROP

    # block new outgoing connection and limit ports
    elif [ "$FIREWALL" = "block_new_conn_output_strict" ]; then
        iptables -A FORWARD -o ${IFACE}_0 -p tcp -m multiport --dports 22,80,443,5000,7000,9050 -j ACCEPT
        iptables -A FORWARD -o ${IFACE}_0 -p tcp -j DROP

        iptables -A FORWARD -o ${IFACE}_0 -p udp -m multiport --dports 53,123,443 -j ACCEPT
        iptables -A FORWARD -o ${IFACE}_0 -p udp -j DROP

        iptables -A FORWARD -i ${IFACE}_0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
        iptables -A FORWARD -i ${IFACE}_0 -j DROP

    elif [ "$FIREWALL" = "block_rsts_output" ]; then
        iptables -A FORWARD -i ${IFACE}_0 -p tcp --tcp-flags ALL RST -j DROP

    elif [ "$FIREWALL" = "block_l4" ]; then
        iptables -A INPUT -i ${IFACE}_0 -p tcp -j DROP
        iptables -A INPUT -i ${IFACE}_0 -p udp -j DROP
        
        iptables -A OUTPUT -o ${IFACE}_0 -p tcp -j DROP
        iptables -A OUTPUT -o ${IFACE}_0 -p udp -j DROP
    fi
done

# Useful iptables commands:
#   iptables --list --verbose
#   iptables --table nat --list --verbose
#   iptables --flush

for IFACE in $IFACES; do
    DROP_PERCENT="$(echo $DROP_PERCENTS | cut -d' ' -f1)"
    DROP_PERCENTS="$(echo $DROP_PERCENTS | cut -d' ' -f2-)"

    DELAY="$(echo $DELAYS | cut -d' ' -f1)"
    DELAYS="$(echo $DELAYS | cut -d' ' -f2-)"

    if [ "$DROP_PERCENT" != "0" ]; then
        tc qdisc add dev ${IFACE}_0 root netem loss ${DROP_PERCENT}%
    fi

    if [ "$DELAY" != "0" ]; then
        tc qdisc add dev ${IFACE}_0 root netem delay ${DELAY}ms
    fi
done

# Useful tc commands:
#   tc qdisc show dev $IFACE
#   tc qdisc del dev $IFACE

# setup congestion control
# for a list of methods, see: sysctl net.ipv4.tcp_allowed_congestion_control
sysctl -w net.ipv4.tcp_congestion_control="$CONGESTION_CONTROL"

# setup syn cookies
if [ "$SYN_COOKIE" = "disable" ]; then
    sysctl -w net.ipv4.tcp_syncookies=0
elif [ "$SYN_COOKIE" = "force" ]; then
    sysctl -w net.ipv4.tcp_syncookies=2
fi

# setup curl
echo "--insecure" > $HOME/.curlrc

# setup nat
for IFACE in $IFACES; do
    NAT="$(echo $NATS | cut -d' ' -f1)"
    NATS="$(echo $NATS | cut -d' ' -f2-)"

    CIDR="$(echo $CIDRS | cut -d' ' -f1)"
    CIDRS="$(echo $CIDRS | cut -d' ' -f2-)"

    if [ "$NAT" = "snat_input" ]; then  # using the input flag is illegal with POSTROUTING
        iptables -t nat -A POSTROUTING -s $CIDR -j MASQUERADE --random
    elif [ "$NAT" = "snat_output" ]; then
        iptables -t nat -A POSTROUTING -o ${IFACE}_0 -j MASQUERADE --random
    fi
done

# setup bird
FILE="/etc/bird.conf"

echo "router id $ID;" > $FILE
echo "log syslog all;" >> $FILE
echo "" >> $FILE # new line
echo "# The Device protocol is not a real routing protocol. It does not generate any" >> $FILE
echo "# routes and it only serves as a module for getting information about network" >> $FILE
echo "# interfaces from the kernel. It is necessary in almost any configuration." >> $FILE
echo "protocol device {}" >> $FILE
echo "" >> $FILE # new line
echo "# The Kernel protocol is not a real routing protocol. Instead of communicating" >> $FILE
echo "# with other routers in the network, it performs synchronization of BIRD" >> $FILE
echo "# routing tables with the OS kernel. One instance per table." >> $FILE
echo "ipv4 table t_master;" >> $FILE
echo "protocol kernel {" >> $FILE
echo -e "\tipv4 {" >> $FILE
echo -e "\t\ttable t_master;" >> $FILE
echo -e "\t\timport all;" >> $FILE
echo -e "\t\texport all;" >> $FILE
echo -e "\t};" >> $FILE
echo "" >> $FILE # new line

# configure ecmp
# may require CONFIG_IP_ROUTE_MULTIPATH on host machine
#   see: `grep CONFIG_IP_ROUTE_MULTIPATH /boot/config-$(uname -r)`

if [ "$ECMP" = "true" ]; then
    sysctl -w net.ipv4.fib_multipath_use_neigh=1
    sysctl -w net.ipv4.fib_multipath_hash_policy=1
    
    echo -e "\tmerge paths on;" >> $FILE
fi

echo -e "\tlearn;" >> $FILE
echo "}" >> $FILE
echo "" >> $FILE # new line
echo "ipv4 table t_ospf;" >> $FILE
echo "protocol ospf v2 {" >> $FILE
echo -e "\tipv4 {" >> $FILE
echo -e "\t\ttable t_ospf;" >> $FILE
echo -e "\t\timport all;" >> $FILE
echo -e "\t\texport all;" >> $FILE
echo -e "\t};" >> $FILE
echo "" >> $FILE # new line
echo -e "\tarea 0.0.0.0 {" >> $FILE

# advertise public interfaces
for IFACE in $IFACES; do
    VISIBILITY="$(echo $VISIBILITIES | cut -d' ' -f1)"
    VISIBILITIES="$(echo $VISIBILITIES | cut -d' ' -f2-)"

    COST="$(echo $COSTS | cut -d' ' -f1)"
    COSTS="$(echo $COSTS | cut -d' ' -f2-)"

    if [ "$VISIBILITY" = "private" ]; then
        continue
    fi

    # must be double quote
    echo -e "\t\tinterface \"${IFACE}_0\" {" >> $FILE
    echo -e "\t\t\ttype broadcast;  # enable automatic router discovery" >> $FILE
    echo -e "\t\t\tcost $COST;" >> $FILE
    echo -e "\t\t};" >> $FILE
done

echo -e "\t};" >> $FILE
echo "}" >> $FILE
echo "" >> $FILE # new line
echo "# The Pipe protocol is not a real routing protocol. It does not generate any" >> $FILE
echo "# routes but synchronizes routes between tables. It is necessary in almost" >> $FILE
echo "# any configuration." >> $FILE
echo "protocol pipe {" >> $FILE
echo -e "\ttable t_ospf;" >> $FILE
echo -e "\tpeer table t_master;" >> $FILE
echo -e "\timport none;" >> $FILE
echo -e "\texport all;" >> $FILE
echo "}" >> $FILE

# run bird
bird
birdc configure

# Useful birdc commands:
#   show protocols
#   show ospf neighbors
#   show route table t_ospf
#   show ospf interface
# Useful ip command:
#   ip route

# sleep
trap "exit 0" SIGTERM
sleep infinity &

wait $!  # $! is the PID of sleep
