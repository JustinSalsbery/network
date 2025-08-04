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
    if [ "$IP" = "none" ]; then  # dhcp
        umount /etc/resolv.conf  # docker mounts resolv.conf
        udhcpc -i ${IFACE}_0     # unmounting allows dhcp to write resolv.conf
    else
        # manual
        ifconfig ${IFACE}_0 $IP netmask $NET_MASK

        if [ "$GATEWAY" != "none" ]; then
            route add default gateway $GATEWAY ${IFACE}_0
        fi
    fi

    # disable tcp segmentation offloading
    # the tcp packet never reaches the NIC and therefore will never segment
    ethtool -K ${IFACE}_0 tso off

    # NIC offloading:
    #   Display: ethtool –k $IFACE
    #   Enable/Disable: ethtool –K $IFACE <setting> <on/off>
done

# setup nameservers
# without dnsmasq, only the first nameserver in resolv.conf will be used
for NAMESERVER in $NAMESERVERS; do
    FILE="/etc/resolv.conf"

    echo "# use dnsmasq for dns resolution" >> $FILE
    echo "nameserver 127.0.0.1  # dnsmasq ignores localhost" >> $FILE
    echo "" >> $FILE  # new line

    if [ "$NAMESERVER" != "none" ]; then
        echo "nameserver $NAMESERVER" >> $FILE
    fi
done

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

# setup congestion control
sysctl -w net.ipv4.tcp_congestion_control="$CONGESTION_CONTROL"

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

# setup hosts
FILE="/etc/dnsmasq.hosts"
echo "" > $FILE  # new line

for HOST_NAME in $HOST_NAMES; do
    HOST_IP="$(echo $HOST_IPS | cut -d' ' -f1)"
    HOST_IPS="$(echo $HOST_IPS | cut -d' ' -f2-)"

    echo "$HOST_IP $HOST_NAME" >> $FILE
done

# setup dns
FILE="/etc/dnsmasq.conf"

echo "no-hosts  # do not use /etc/hosts" > $FILE
echo "addn-hosts=/etc/dnsmasq.hosts" >> $FILE
echo "local-ttl=$TTL  # seconds" >> $FILE
echo "" >> $FILE  # new line
echo "# if the record is not found locally, forward to all nameservers" >> $FILE
echo "# by default, dnsmasq and resolv only forward to the first nameserver" >> $FILE
echo "all-servers" >> $FILE
echo "" >> $FILE  # new line
echo "# without filtering, AAAA requests will return a REFUSED error" >> $FILE
echo "# various utilities, such as socket.getaddrinfo, will throw a gaierror in response" >> $FILE
echo "filter-AAAA  # return a FILTERED response" >> $FILE
echo "" >> $FILE  # new line

if [ "$LOG" = "true" ]; then
    echo "log-queries" >> $FILE
    echo "log-facility=/app/dns.log" >> $FILE
fi

dnsmasq  # run

# Useful commands:
#   Query A    record (IPv4): dig <DOMAIN NAME>
#   Query AAAA record (IPv6): dig aaaa <DOMAIN NAME>

# sleep
trap "exit 0" SIGTERM
sleep infinity &

wait $!  # $! is the PID of sleep
