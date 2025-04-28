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

# sleep
trap "exit 0" SIGTERM
sleep infinity &

wait $!  # $! is the PID of sleep


"""
protocol ospf v2 {
    ipv4 {
        import none;
        export all;
    }
  
    area 0.0.0.0 {
        interface "eth0" { type broadcast; };
    };
}
"""

# https://www.haproxy.com/documentation/haproxy-configuration-manual/3-0r1/
# http://haproxy.1wt.eu/download/1.5/doc/configuration.txt

global
    daemon

    # option httplog    # better logging
    # log stderr local0 # log to stderr

frontend http
    bind *:80  accept-proxy
    bind *:443 accept-proxy ssl crt /app/ssl/cert.pem ssl-min-ver TLSv1.2

    # ssl crt default should only be used in http mode
    mode tcp  # tcp, http

    default_backend servers

backend servers
    mode tcp  # tcp, http
    # source is deterministic, all LBs will route the same
    # all others are non-deterministic
    balance source        # roundrobin, random, leastconn, source
    hash-type consistent  # use with source only

    option httpchk /
    check-ssl

    # the backend uses https for all traffic
    server server_1 192.168.0.1:443 send-proxy check ssl verify none
    server server_2 192.168.0.2:443 send-proxy check ssl verify none

# haproxy -f /etc/haproxy/haproxy.cfg
