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
for IFACE in $IFACES; do
    RATE="$(echo $RATES | cut -d' ' -f1)"
    RATES="$(echo $RATES | cut -d' ' -f2-)"

    MTU="$(echo $MTUS | cut -d' ' -f1)"
    MTUS="$(echo $MTUS | cut -d' ' -f2-)"

    QUEUE_TIME="$(echo $QUEUE_TIMES | cut -d' ' -f1)"
    QUEUE_TIMES="$(echo $QUEUE_TIMES | cut -d' ' -f2-)"

    BURST="$(echo $BURSTS | cut -d' ' -f1)"
    BURSTS="$(echo $BURSTS | cut -d' ' -f2-)"

    tc qdisc add dev ${IFACE}_0 root tbf rate ${RATE}mbit burst ${BURST}kbit \
        latency ${QUEUE_TIME}ms  # mtu option does not seem to work
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

    # for endpoints, add rules to output/input table

    # routing protocols, vpns, k8s, databases, etc are unaccounted for
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

for IFACE in $IFACES; do
    DROP="$(echo $DROPS | cut -d' ' -f1)"
    DROPS="$(echo $DROPS | cut -d' ' -f2-)"

    DELAY="$(echo $DELAYS | cut -d' ' -f1)"
    DELAYS="$(echo $DELAYS | cut -d' ' -f2-)"

    if [ "$DROP" != "0" ]; then
        tc qdisc add dev ${IFACE}_0 root netem loss ${DROP}%
    fi

    if [ "$DELAY" != "0" ]; then
        tc qdisc add dev ${IFACE}_0 root netem delay ${DELAY}ms
    fi
done

# Useful tc commands:
#   tc qdisc list
#   tc qdisc del dev $IFACE root

# setup congestion control
sysctl -w net.ipv4.tcp_congestion_control="$CONGESTION_CONTROL"

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

# setup locust
OUT="shared/locust-$HOSTNAME.csv"
FILE="locustfile.py"

echo "from locust import FastHttpUser, between, task" > $FILE
echo "from time import sleep" >> $FILE
echo "" >> $FILE  # new line
echo "sleep(60)  # seconds; allow routers time to configure" >> $FILE
echo "" >> $FILE  # new line
echo "class WebsiteUser(FastHttpUser):" >> $FILE
echo -e "\thost = '$PROTO://$TARGET'" >> $FILE
echo -e "\twait_time = between($WAIT_MIN, $WAIT_MAX)" >> $FILE
echo "" >> $FILE  # new line
echo -e "\t@task($CONN_DUR)" >> $FILE
echo -e "\tdef request(self):" >> $FILE

if [ "$GZIP" = "true" ]; then
    echo -e "\t\theaders = {'Accept-Encoding': 'gzip'}" >> $FILE
else
    echo -e "\t\theaders = {'Accept-Encoding': 'identity'}  # no compression" >> $FILE
fi

for REQUEST in $REQUESTS; do
    echo -e "\t\tself.client.get('$REQUEST', headers=headers)" >> $FILE
done

echo "" >> $FILE  # new line
echo -e "\t@task(1)" >> $FILE
echo -e "\tdef close(self):" >> $FILE
echo -e "\t\tself.client.client.close()" >> $FILE

# run locust
trap "pkill locust" SIGTERM
locust -f $FILE --headless -u $CONN_MAX -r $CONN_RATE --csv-full-history \
    --csv csv/results 2> /dev/null &  # locust outputs traffic details to stderr

wait $!  # $! is the PID of locust
cp csv/results_stats_history.csv $OUT
