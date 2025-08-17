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

    MTU="$(echo $MTUS | cut -d' ' -f1)"
    MTUS="$(echo $MTUS | cut -d' ' -f2-)"

    GATEWAY="$(echo $GATEWAYS | cut -d' ' -f1)"
    GATEWAYS="$(echo $GATEWAYS | cut -d' ' -f2-)"

    # network suffix should be _0
    if [ "$IP" = "none" ]; then  # dhcp
        # docker mounts resolv.conf and unmounting is required to write
        umount /etc/resolv.conf

        # if dhcp fails, the interface does not exist
        udhcpc -i ${IFACE}_0 -t 25 -n || continue
    else # manual
        ifconfig ${IFACE}_0 $IP netmask $NET_MASK
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
if [ "$NAMESERVER" != "none" ]; then
    FILE="/etc/resolv.conf"  # delete in case resolv was configured by dhcp
    echo "# only the first nameserver will be used" > $FILE

    for NAMESERVER in $NAMESERVERS; do
        echo "nameserver $NAMESERVER" >> $FILE
    done
fi

# setup tc rules
# each interface may have one tc rule
for IFACE in $IFACES; do
    TC_RULE="$(echo $TC_RULES | cut -d' ' -f1)"
    TC_RULES="$(echo $TC_RULES | cut -d' ' -f2-)"

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

    if [ "$TC_RULE" = "rate" ]; then
        tc qdisc add dev ${IFACE}_0 root netem limit ${QUEUE_LIMIT} rate ${RATE}kbit
    elif [ "$TC_RULE" = "delay" ]; then
        tc qdisc add dev ${IFACE}_0 root netem limit ${QUEUE_LIMIT} delay ${DELAY}ms ${JITTER}ms
    elif [ "$TC_RULE" = "drop" ]; then
        tc qdisc add dev ${IFACE}_0 root netem limit ${QUEUE_LIMIT} loss random ${DROP}%
    elif [ "$TC_RULE" = "corrupt" ]; then
        tc qdisc add dev ${IFACE}_0 root netem limit ${QUEUE_LIMIT} corrupt ${CORRUPT}%
    elif [ "$TC_RULE" = "duplicate" ]; then
        tc qdisc add dev ${IFACE}_0 root netem limit ${QUEUE_LIMIT} duplicate ${DUPLICATE}%
    fi
done

# Useful tc commands:
#   tc qdisc list
#   tc qdisc del dev $IFACE root

# setup firewall
for IFACE in $IFACES; do
    FIREWALL="$(echo $FIREWALLS | cut -d' ' -f1)"
    FIREWALLS="$(echo $FIREWALLS | cut -d' ' -f2-)"

    # for endpoints, add rules to output/input table
    # limit ports:
    #   - tcp: 22 (ssh), 80 (http), 443 (https), 5000 (tor node), 7000 (tor directory), 9050 (tor socks)
    #   - udp: 53 (dns), 67 (dhcp), 123 (ntp), 443 (quic)

    # block new incoming connections; internal endpoints must initiate all connections
    if [ "$FIREWALL" = "block_new_conn_input" ]; then
        iptables -A INPUT -i ${IFACE}_0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
        iptables -A INPUT -i ${IFACE}_0 -j DROP

    # block new incoming connections and limit ports
    elif [ "$FIREWALL" = "block_new_conn_input_strict" ]; then
        iptables -A OUTPUT -o ${IFACE}_0 -p tcp -m multiport --dports 22,80,443,5000,7000,9050 -j ACCEPT
        iptables -A OUTPUT -o ${IFACE}_0 -p tcp -j DROP

        iptables -A OUTPUT -o ${IFACE}_0 -p udp -m multiport --dports 53,67,123,443 -j ACCEPT
        iptables -A OUTPUT -o ${IFACE}_0 -p udp -j DROP

        iptables -A INPUT -i ${IFACE}_0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
        iptables -A INPUT -i ${IFACE}_0 -j DROP

    # block new outgoing connections; external endpoints must initiate all connections
    elif [ "$FIREWALL" = "block_new_conn_output" ]; then
        iptables -A OUTPUT -o ${IFACE}_0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
        iptables -A OUTPUT -o ${IFACE}_0 -j DROP

    # block new outgoing connection and limit ports
    elif [ "$FIREWALL" = "block_new_conn_output_strict" ]; then
        iptables -A INPUT -i ${IFACE}_0 -p tcp -m multiport --dports 22,80,443,5000,7000,9050 -j ACCEPT
        iptables -A INPUT -i ${IFACE}_0 -p tcp -j DROP

        iptables -A INPUT -i ${IFACE}_0 -p udp -m multiport --dports 53,67,123,443 -j ACCEPT
        iptables -A INPUT -i ${IFACE}_0 -p udp -j DROP

        iptables -A OUTPUT -o ${IFACE}_0 -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
        iptables -A OUTPUT -o ${IFACE}_0 -j DROP

    elif [ "$FIREWALL" = "block_rsts_output" ]; then
        iptables -A OUTPUT -o ${IFACE}_0 -p tcp --tcp-flags ALL RST -j DROP
    
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

nginx  # run

# sleep
trap "exit 0" SIGTERM
sleep infinity &

wait $!  # $! is the PID of sleep
