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

# setup shared
mkdir -p shared/$HOSTNAME/
chmod 666 shared/$HOSTNAME/

# setup tor
# configured for a single interface
DATA_DIR="/var/lib/tor/"
LOG_DIR="/app/shared/$HOSTNAME/"

for IFACE in $IFACES; do
    IP="$(echo $IPS | cut -d' ' -f1)"
    IPS="$(echo $IPS | cut -d' ' -f2-)"

    # if tor creates the data directory, the directory will be owned by the tor account
    # we are running tor with the root account, which will result in errors
    rm -rf $DATA_DIR
    mkdir -p $DATA_DIR

    echo $IP > shared/$HOSTNAME/ip

    # setup certificate
    # cert is only necessary for directory authority
    echo "eastern" > $DATA_DIR/password
    exec 3<> $DATA_DIR/password  # open password as file descriptor 3

    tor-gencert --passphrase-fd 3 --create-identity-key -m 12 -a $IP:7000 -i $DATA_DIR/keys/authority_identity_key -s $DATA_DIR/keys/authority_signing_key -c $DATA_DIR/keys/authority_certificate
    cat $DATA_DIR/authority_certificate | grep fingerprint | cut -d' ' -f2 > shared/$HOSTNAME/certificate

    exec 3>&-  # close file descriptor 3

    # setup fingerprint
    tor --list-fingerprint --orport 1 --dirserver "x 127.0.0.1:1 ffffffffffffffffffffffffffffffffffffffff" --datadirectory $DATA_DIR
    cat $DATA_DIR/fingerprint | cut -d' ' -f2 > shared/$HOSTNAME/fingerprint

    # wait for directory authority
    # if the node is a directory authority, the node will read it's own information
    while ! [ -f "shared/$TOR_AUTH/ready" ]; then
        echo "waiting for $TOR_AUTH to write to shared/"
        sleep 1  # seconds
    fi

    AUTH_IP="$(cat shared/$TOR_AUTH/ip)"
    AUTH_CERT="$(cat shared/$TOR_AUTH/certificate)"
    AUTH_FINGERPRINT="$(cat shared/$TOR_AUTH/fingerprint)"

    # setup torrc
    FILE="/etc/tor/torrc"

    echo "DataDirectory $DATA_DIR" > $FILE
    echo "TestingTorNetwork 1" >> $FILE
    echo "DirAuthority $TOR_AUTH no-v2 v3ident=$AUTH_CERT $AUTH_IP:7000 $AUTH_FINGERPRINT orport=5000" >> $FILE
    echo "" >> $FILE  # new line
    echo "RunAsDaemon 0" >> $FILE
    echo "ShutdownWaitLength 0" >> $FILE
    echo "" >> $FILE  # new line
    echo "AssumeReachable 1" >> $FILE
    echo "PathsNeededToBuildCircuits 0.25" >> $FILE
    echo "" >> $FILE  # new line
    echo "# Remove requirements" >> $FILE
    echo "TestingDirAuthVoteGuard *" >> $FILE
    echo "TestingDirAuthVoteExit *" >> $FILE
    echo "TestingDirAuthVoteHSDir *" >> $FILE
    echo "" >> $FILE  # new line
    echo "SafeLogging 0" >> $FILE
    echo "Log notice file $LOG_DIR/notice.log" >> $FILE
    echo "Log info file $LOG_DIR/info.log" >> $FILE
    echo "Log debug file $LOG_DIR/debug.log" >> $FILE
    echo "" >> $FILE  # new line
    echo "Nickname $HOSTNAME" >> $FILE
    echo "Address $IP" >> $FILE
    echo "ContactInfo $HOSTNAME@ewu.edu" >> $FILE
    echo "" >> $FILE  # new line
    echo "SocksPort 0" >> $FILE
    echo "OrPort 5000" >> $FILE
    echo "DirPort 7000" >> $FILE
    echo "" >> $FILE  # new line

    if [ "$TOR_BRIDGE" = "true" ]; then
        echo "BridgeRelay 1" >> $FILE
    else
        echo "BridgeRelay 0" >> $FILE
    fi

    if [ "$TOR_EXIT" = "true" ]; then
        echo "ExitRelay 1" >> $FILE
    else
        echo "ExitRelay 0" >> $FILE
    fi

    if [ "$TOR_AUTH" = "$HOSTNAME" ]; then
        echo "" >> $FILE  # new line
        echo "AuthoritativeDirectory 1" >> $FILE
        echo "V3AuthoritativeDirectory 1" >> $FILE
        echo "BridgeAuthoritativeDir 1" >> $FILE
    fi
done

# run
trap "exit 0" SIGTERM

if [ "$AUTO_RESTART" = "true" ]; then
    tor &
else
    tor &
    sleep infinity &
fi

echo "" > shared/$HOSTNAME/ready
wait $!
