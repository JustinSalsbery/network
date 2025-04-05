#!/bin/sh

# setup ifaces
for IFACE in $IFACES; do
    SRC_IP="$(echo $SRC_IPS | cut -d' ' -f1)"  # the first index
    SRC_IPS="$(echo $SRC_IPS | cut -d' ' -f2-)"  # the rest of the list

    NET_MASK="$(echo $NET_MASKS | cut -d' ' -f1)"
    NET_MASKS="$(echo $NET_MASKS | cut -d' ' -f2-)"

    GATEWAY="$(echo $GATEWAYS | cut -d' ' -f1)"
    GATEWAYS="$(echo $GATEWAYS | cut -d' ' -f2-)"

    # network suffix should be _0
    ifconfig ${IFACE}_0 $SRC_IP netmask $NET_MASK || \
        echo "error: Failed to configure ${IFACE}_0"
    
    if [ "$GATEWAY" != "none" ]; then
        route add default gateway $GATEWAY ${IFACE}_0 || \
            echo "error: Failed to configure the gateway for ${IFACE}_0"
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
OUT="/etc/bird.conf"

echo "log syslog all;" > $OUT
echo "" >> $OUT # new line
echo "# The Device protocol is not a real routing protocol. It does not generate any" >> $OUT
echo "# routes and it only serves as a module for getting information about network" >> $OUT
echo "# interfaces from the kernel. It is necessary in almost any configuration." >> $OUT
echo "protocol device {}" >> $OUT
echo "" >> $OUT # new line
echo "# The Kernel protocol is not a real routing protocol. Instead of communicating" >> $OUT
echo "# with other routers in the network, it performs synchronization of BIRD" >> $OUT
echo "# routing tables with the OS kernel. One instance per table." >> $OUT
echo "ipv4 table t_master;" >> $OUT
echo "protocol kernel {" >> $OUT
echo -e "\tipv4 {" >> $OUT
echo -e "\t\ttable t_master;" >> $OUT
echo -e "\t\timport all;" >> $OUT
echo -e "\t\texport all;" >> $OUT
echo -e "\t};" >> $OUT
echo "" >> $OUT # new line

# configure ecmp
# may require CONFIG_IP_ROUTE_MULTIPATH on host machine
#   see: `grep CONFIG_IP_ROUTE_MULTIPATH /boot/config-$(uname -r)`

if [ "$ECMP" = "true" ]; then
    sysctl net.ipv4.fib_multipath_use_neigh=1
    sysctl net.ipv4.fib_multipath_hash_policy=1
    
    echo -e "\tmerge paths on;" >> $OUT
fi

echo -e "\tlearn;" >> $OUT
echo "}" >> $OUT
echo "" >> $OUT # new line
echo "ipv4 table t_ospf;" >> $OUT
echo "protocol ospf v2 {" >> $OUT
echo -e "\tipv4 {" >> $OUT
echo -e "\t\ttable t_ospf;" >> $OUT
echo -e "\t\timport all;" >> $OUT
echo -e "\t\texport all;" >> $OUT
echo -e "\t};" >> $OUT
echo "" >> $OUT # new line
echo -e "\tarea 0.0.0.0 {" >> $OUT

# advertise public interfaces
for IFACE in $IFACES; do
    VISIBILITY="$(echo $VISIBILITIES | cut -d' ' -f1)"
    VISIBILITIES="$(echo $VISIBILITIES | cut -d' ' -f2-)"

    if [ "$VISIBILITY" = "private" ]; then
        continue
    fi

    # must be double quote
    echo -e "\t\tinterface \"${IFACE}_0\" { type broadcast; };" >> $OUT
done

echo -e "\t};" >> $OUT
echo "}" >> $OUT
echo "" >> $OUT # new line
echo "# The Pipe protocol is not a real routing protocol. It does not generate any" >> $OUT
echo "# routes but synchronizes routes between tables. It is necessary in almost" >> $OUT
echo "# any configuration." >> $OUT
echo "protocol pipe {" >> $OUT
echo -e "\ttable t_ospf;" >> $OUT
echo -e "\tpeer table t_master;" >> $OUT
echo -e "\timport none;" >> $OUT
echo -e "\texport all;" >> $OUT
echo "}" >> $OUT

# run bird
bird
birdc configure

# Useful birdc commands:
#   show protocols
#   show ospf neighbors
#   show route table t_ospf
# Useful ip command:
#   ip route

# sleep
trap "exit 0" SIGTERM
sleep infinity &

wait $!  # $! is the PID of sleep
