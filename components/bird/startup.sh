#!/bin/sh

# delete docker configurations
echo "127.0.0.1 localhost" > /etc/hosts
echo "" > /etc/resolv.conf

# disable ipv6
sysctl -w net.ipv6.conf.all.disable_ipv6=1

# setup ifaces
for IFACE in $IFACES; do
    IP="$(echo $IPS | cut -d' ' -f1)"    # the first index
    IPS="$(echo $IPS | cut -d' ' -f2-)"  # the rest of the list

    NET_MASK="$(echo $NET_MASKS | cut -d' ' -f1)"
    NET_MASKS="$(echo $NET_MASKS | cut -d' ' -f2-)"

    MTU="$(echo $MTUS | cut -d' ' -f1)"
    MTUS="$(echo $MTUS | cut -d' ' -f2-)"

    GATEWAY="$(echo $GATEWAYS | cut -d' ' -f1)"
    GATEWAYS="$(echo $GATEWAYS | cut -d' ' -f2-)"

    # network suffix should be _0
    if [ "$IP" = "none" ]; then  # dhcp
        # docker mounts resolv.conf and unmounting is required to write
        umount /etc/resolv.conf

        # if dhcp fails, the interface is not configured
        udhcpc -i ${IFACE}_0 -t 25 -n || \
            ifconfig ${IFACE}_0 down && continue
    else # manual
        ifconfig ${IFACE}_0 $IP
    fi

    if [ "$NET_MASK" != "none" ]; then
        ifconfig ${IFACE}_0 netmask $NET_MASK
    fi

    if [ "$MTU" != "none" ]; then
        # the tcp packet never reaches the NIC and therefore will never segment
        ethtool -K ${IFACE}_0 tso off # disable tcp segmentation offloading

        ifconfig ${IFACE}_0 mtu $MTU
    fi

    if [ "$GATEWAY" != "none" ]; then
        route add default gateway $GATEWAY ${IFACE}_0
    fi
done

# NIC offloading:
#   Display: ethtool –k $IFACE
#   Enable/Disable: ethtool –K $IFACE <setting> <on/off>

# setup nameservers
if [ "$NAMESERVERS" != "none" ]; then
    FILE="/etc/resolv.conf"  # delete in case resolv was configured by dhcp
    echo "# only the first nameserver will be used" > $FILE

    for NAMESERVER in $NAMESERVERS; do
        echo "nameserver $NAMESERVER" >> $FILE
    done
fi

# setup tc rules
# each interface may have one tc rule
for IFACE in $IFACES; do
    RATE="$(echo $RATES | cut -d' ' -f1)"
    RATES="$(echo $RATES | cut -d' ' -f2-)"

    DELAY="$(echo $DELAYS | cut -d' ' -f1)"
    DELAYS="$(echo $DELAYS | cut -d' ' -f2-)"

    JITTER="$(echo $JITTERS | cut -d' ' -f1)"
    JITTERS="$(echo $JITTERS | cut -d' ' -f2-)"

    DROP="$(echo $DROPS | cut -d' ' -f1)"
    DROPS="$(echo $DROPS | cut -d' ' -f2-)"

    CORRUPT="$(echo $CORRUPTS | cut -d' ' -f1)"
    CORRUPTS="$(echo $CORRUPTS | cut -d' ' -f2-)"

    DUPLICATE="$(echo $DUPLICATES | cut -d' ' -f1)"
    DUPLICATES="$(echo $DUPLICATES | cut -d' ' -f2-)"

    QUEUE_LIMIT="$(echo $QUEUE_LIMITS | cut -d' ' -f1)"
    QUEUE_LIMITS="$(echo $QUEUE_LIMITS | cut -d' ' -f2-)"

    # tc ignores arguments of 0, except for QUEUE_LIMIT
    if [ "$QUEUE_LIMIT" != "none" ]; then
        tc qdisc add dev ${IFACE}_0 root netem limit ${QUEUE_LIMIT} rate ${RATE}kbit \
        delay ${DELAY}ms ${JITTER}ms loss random ${DROP}% corrupt ${CORRUPT}% duplicate ${DUPLICATE}%
    fi
done

# Useful tc commands:
#   tc qdisc list
#   tc qdisc del dev $IFACE root

# setup firewall
for IFACE in $IFACES; do
    FIREWALL="$(echo $FIREWALLS | cut -d' ' -f1)"
    FIREWALLS="$(echo $FIREWALLS | cut -d' ' -f2-)"

    # for routers, add rules to forwarding table
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

# kernel options: https://www.kernel.org/doc/html/latest/networking/ip-sysctl.html

# setup congestion control
sysctl -w net.ipv4.tcp_congestion_control="$CONGESTION_CONTROL"

# setup ttl
sysctl -w net.ipv4.ip_default_ttl=$TTL

# setup forwarding
if [ "$FORWARD" = "true" ]; then
    sysctl -w net.ipv4.ip_forward=1
else
    sysctl -w net.ipv4.ip_forward=0
fi

# setup syn cookies
if [ "$SYN_COOKIE" = "disable" ]; then
    sysctl -w net.ipv4.tcp_syncookies=0
elif [ "$SYN_COOKIE" = "enable" ]; then
    sysctl -w net.ipv4.tcp_syncookies=1
elif [ "$SYN_COOKIE" = "force" ]; then
    sysctl -w net.ipv4.tcp_syncookies=2
fi

# setup fast retransmission
if [ "$FAST_RETRAN" = "true" ]; then
    sysctl -w net.ipv4.tcp_early_retrans=3  # after 3 packets
else
    sysctl -w net.ipv4.tcp_early_retrans=0
fi

# setup selective acknowledgments
if [ "$SACK" = "true" ]; then
    sysctl -w net.ipv4.tcp_sack=1
else
    sysctl -w net.ipv4.tcp_sack=0
fi

# setup timestamps
if [ "$TIMESTAMP" = "true" ]; then
    sysctl -w net.ipv4.tcp_timestamps=1
else
    sysctl -w net.ipv4.tcp_timestamps=0
fi

# setup curl
echo "--insecure" > $HOME/.curlrc  # allow self-signed certificates
echo "--verbose" >> $HOME/.curlrc

# setup shared
mkdir -p shared/$HOSTNAME/
chmod 666 shared/$HOSTNAME/

# configure ecmp
if [ "$ECMP" = "l3" ]; then
    sysctl -w net.ipv4.fib_multipath_hash_policy=0
    sysctl -w net.ipv4.fib_multipath_use_neigh=1
elif [ "$ECMP" = "l4" ]; then
    sysctl -w net.ipv4.fib_multipath_hash_policy=1
    sysctl -w net.ipv4.fib_multipath_use_neigh=1
fi

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

echo "router id $ROUTER_ID;" > $FILE
echo "log \"shared/${HOSTNAME}/bird.log\" all;" >> $FILE
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

if [ "$ECMP" != "none" ]; then    
    echo -e "\tmerge paths on;" >> $FILE
fi

echo -e "\tlearn;" >> $FILE
echo "}" >> $FILE
echo "" >> $FILE # new line
echo "filter martians" >> $FILE
echo "{" >> $FILE
echo -e "\t# subset of martians defined in rfc 1918" >> $FILE
echo -e "\tif net ~ [ 10.0.0.0/8+, 169.254.0.0/16+, 172.16.0.0/12+, 192.168.0.0/16+ ]" >> $FILE
echo -e "\t\tthen reject;" >> $FILE
echo -e "\taccept;" >> $FILE
echo "}" >> $FILE
echo "" >> $FILE # new line
echo "ipv4 table t_ospf;" >> $FILE
echo "protocol ospf v2 {" >> $FILE
echo -e "\tipv4 {" >> $FILE
echo -e "\t\ttable t_ospf;" >> $FILE
echo -e "\t\timport filter martians;" >> $FILE
echo -e "\t\texport all;" >> $FILE
echo -e "\t};" >> $FILE
echo "" >> $FILE # new line

if [ "$ECMP" != "none" ]; then    
    echo -e "\tecmp on;" >> $FILE
    echo -e "\tmerge external on;" >> $FILE
fi

echo "" >> $FILE # new line
echo -e "\tarea 0.0.0.0 {" >> $FILE

for IFACE in $IFACES; do
    COST="$(echo $COSTS | cut -d' ' -f1)"
    COSTS="$(echo $COSTS | cut -d' ' -f2-)"

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
echo "" >> $FILE # new line
echo -e "\timport none;" >> $FILE
echo -e "\texport all;" >> $FILE
echo "}" >> $FILE

# run
trap "exit 0" SIGTERM

if [ "$AUTO_RESTART" = "true" ]; then
    bird -f &
else
    bird
    sleep infinity &
fi

wait $!

# Useful birdc commands:
#   show protocols
#   show ospf neighbors
#   show route table t_ospf
#   show ospf interface
# Useful ip command:
#   ip route
