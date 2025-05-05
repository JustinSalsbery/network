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
    fi
done

# setup nameservers
# without dnsmasq, only the first nameserver in resolv.conf will be used
for NAMESERVER in $NAMESERVERS; do
    if [ "$NAMESERVER" != "none" ]; then
        echo "nameserver $NAMESERVER" >> /etc/resolv.conf
    fi
done

# setup iface queue
# each interface may only have a single tc rule
# tc rules will overwrite each other so that only the last tc rule will apply
for IFACE in $IFACES; do
    RATE="$(echo $RATES | cut -d' ' -f1)"
    RATES="$(echo $RATES | cut -d' ' -f2-)"

    QUEUE_TIME="$(echo $QUEUE_TIMES | cut -d' ' -f1)"
    QUEUE_TIMES="$(echo $QUEUE_TIMES | cut -d' ' -f2-)"

    BURST="$(echo $BURSTS | cut -d' ' -f1)"
    BURSTS="$(echo $BURSTS | cut -d' ' -f2-)"

    tc qdisc add dev ${IFACE}_0 root tbf rate ${RATE}mbit burst ${BURST}kbit \
        latency ${QUEUE_TIME}ms
done

# setup iface behaviors
for IFACE in $IFACES; do
    DELAY="$(echo $DELAYS | cut -d' ' -f1)"
    DELAYS="$(echo $DELAYS | cut -d' ' -f2-)"

    DROP="$(echo $DROPS | cut -d' ' -f1)"
    DROPS="$(echo $DROPS | cut -d' ' -f2-)"

    CORRUPT="$(echo $CORRUPTS | cut -d' ' -f1)"
    CORRUPTS="$(echo $CORRUPTS | cut -d' ' -f2-)"

    if [ "$DELAY" != "0" ]; then
        # the limit is the number of packets that the queue may hold at once
        # the default is 1,000 packets, but that is not enough with a large delay
        LIMIT=$((1000 + (1000 * $DELAYS / 50)))  # seems reasonable

        tc qdisc add dev ${IFACE}_0 root netem limit $LIMIT delay ${DELAY}ms
    fi

    if [ "$DROP" != "0" ]; then  # line rate
        tc qdisc add dev ${IFACE}_0 root netem loss random ${DROP}%
    fi

    if [ "$CORRUPT" != "0" ]; then  # line rate
        tc qdisc add dev ${IFACE}_0 root netem corrupt ${CORRUPT}%
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
if [ "$FAST_RETRANS" = "true" ]; then
    sysctl -w net.ipv4.tcp_early_retrans=3  # after 3 packets
else
    sysctl -w net.ipv4.tcp_early_retrans=0
fi

# setup selective acknowledgments
if [ "$SACKS" = "true" ]; then
    sysctl -w net.ipv4.tcp_sack=1
else
    sysctl -w net.ipv4.tcp_sack=0
fi

# setup timestamps
if [ "$TIMESTAMPS" = "true" ]; then
    sysctl -w net.ipv4.tcp_timestamps=1
else
    sysctl -w net.ipv4.tcp_timestamps=0
fi

# setup curl
echo "--insecure" > $HOME/.curlrc

# setup bird
# haproxy is not a router; advertise the route, but do not import any routes
FILE="/etc/bird.conf"

if [ "$ADVERTISE" = "true" ]; then
    echo "router id $ID;" > $FILE
    echo "log syslog all;" >> $FILE
    echo "" >> $FILE # new line
    echo "# Device is required by bird to query for interface information." >> $FILE
    echo "protocol device {}" >> $FILE
    echo "" >> $FILE # new line
    echo "ipv4 table t_ospf;" >> $FILE
    echo "protocol ospf v2 {" >> $FILE
    echo -e "\tipv4 {" >> $FILE
    echo -e "\t\ttable t_ospf;" >> $FILE
    echo -e "\t\timport none;" >> $FILE
    echo -e "\t\texport all;" >> $FILE
    echo -e "\t};" >> $FILE
    echo "" >> $FILE # new line
    echo -e "\tarea 0.0.0.0 {" >> $FILE

    for IFACE in $IFACES; do
        # must be double quote
        echo -e "\t\tinterface \"${IFACE}_0\" {" >> $FILE
        echo -e "\t\t\ttype broadcast;  # enable automatic router discovery" >> $FILE
        echo -e "\t\t};" >> $FILE
    done

    echo -e "\t};" >> $FILE
    echo "}" >> $FILE

    # run bird
    bird
    birdc configure
fi

# Useful birdc commands:
#   show protocols
#   show ospf neighbors
#   show route table t_ospf
#   show ospf interface
# Useful ip command:
#   ip route

FILE="/etc/haproxy/haproxy.cfg"

echo "defaults" > $FILE

if [ "$TYPE" == "l4" ]; then
    echo -e "\tmode tcp" >> $FILE
elif [ "$TYPE" == "l5" ]; then
    echo -e "\tmode http" >> $FILE
fi

echo "" >> $FILE  # new line
echo -e "\ttimeout connect 10s" >> $FILE
echo -e "\ttimeout client 30s  # client and server must be equivalent in tcp mode"  >> $FILE
echo -e "\ttimeout server 30s"  >> $FILE
echo "" >> $FILE  # new line
echo "frontend http" >> $FILE
echo -e "\tbind *:80" >> $FILE
echo -e "\tdefault_backend http_servers" >> $FILE
echo "" >> $FILE  # new line
echo "frontend https" >> $FILE

if [ "$TYPE" == "l4" ]; then
    echo -e "\tbind *:443" >> $FILE
elif [ "$TYPE" == "l5" ]; then
    echo -e "\t# enable ssl termination" >> $FILE
    echo -e "\tbind *:443 ssl crt /app/ssl/cert.pem ssl-min-ver TLSv1.2 no-tls-tickets" >> $FILE
fi

echo -e "\tdefault_backend https_servers" >> $FILE
echo "" >> $FILE  # new line
echo "backend http_servers" >> $FILE
echo -e "\tbalance $ALGORITHM" >> $FILE

if [ "$ALGORITHM" == "source" ]; then
    echo -e "\thash-type consistent  # deterministic routing" >> $FILE
elif [ "$TYPE" == "l4" ]; then
    echo -e "\tstick-table type ip size 5m expire 10m  # 50 bytes per entry" >> $FILE
    echo -e "\tstick on src  # tcp must be sticky; use lookup table" >> $FILE
elif [ "$TYPE" == "l5" ]; then
    echo -e "\t# non-determinism will cause issues if segmentation occurs from the client" >> $FILE
fi

echo "" >> $FILE  # new line
echo -e "\toption httpchk GET $CHECK" >> $FILE
echo ""  >> $FILE  # new line

i=0
for BACKEND in $BACKENDS; do
    echo -e "\tserver server_$i $BACKEND:80 check" >> $FILE
    i=$((i + 1))
done

echo "" >> $FILE  # new line
echo "backend https_servers" >> $FILE
echo -e "\tbalance $ALGORITHM" >> $FILE

if [ "$ALGORITHM" == "source" ]; then
    echo -e "\thash-type consistent  # deterministic routing" >> $FILE
elif [ "$TYPE" == "l4" ]; then
    echo -e "\tstick-table type ip size 5m expire 10m  # 50 bytes per entry" >> $FILE
    echo -e "\tstick on src  # tcp must be sticky; use lookup table" >> $FILE
elif [ "$TYPE" == "l5" ]; then
    echo -e "\t# non-determinism will cause issues if segmentation occurs from the client" >> $FILE
fi

echo "" >> $FILE  # new line
echo -e "\toption httpchk GET $CHECK" >> $FILE
echo -e "\t# health checks must use ssl" >> $FILE
echo ""  >> $FILE  # new line

i=0
if [ "$TYPE" == "l4" ]; then
    for BACKEND in $BACKENDS; do
        echo -e "\tserver server_$i $BACKEND:443 check check-ssl verify none" >> $FILE
        i=$((i + 1))
    done
elif [ "$TYPE" == "l5" ]; then
    echo -e "\t# traffic must be re-encrypted" >> $FILE
    echo -e "\t# frequently a shorter, less-secure key will be used to increase performance" >> $FILE
    echo ""  >> $FILE  # new line

    for BACKEND in $BACKENDS; do
        echo -e "\tserver server_$i $BACKEND:443 check ssl verify none" >> $FILE
        i=$((i + 1))
    done
fi

haproxy -f $FILE &  # run haproxy

# sleep
trap "exit 0" SIGTERM
sleep infinity &

wait $!  # $! is the PID of sleep
