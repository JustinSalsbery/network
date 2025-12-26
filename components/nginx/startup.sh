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

# setup logs
mkdir -p logs/$HOSTNAME/
chmod 666 logs/$HOSTNAME/

# setup tor
# configured for a single interface
if ! [ "$TOR_DIR" = "" ]; then
    DATA_DIR="/var/lib/tor/"
    LOG_DIR="/app/logs/$HOSTNAME/"

    for IFACE in $IFACES; do
        IP="$(echo $IPS | cut -d' ' -f1)"
        IPS="$(echo $IPS | cut -d' ' -f2-)"

        # if tor creates the data directory, the directory will be owned by the tor account
        # we are running tor with the root account, which will result in errors
        rm -rf $DATA_DIR
        mkdir -p $DATA_DIR/www

        # wait for directory authority
        while ! [ -f "logs/$TOR_DIR/ready" ]; do
            echo "waiting for logs/$TOR_DIR/ready"
            sleep 3  # seconds
        done

        AUTH_IP="$(cat logs/$TOR_DIR/ip)"
        AUTH_CERT="$(cat logs/$TOR_DIR/certificate)"
        AUTH_FINGERPRINT="$(cat logs/$TOR_DIR/fingerprint)"

        # setup torrc
        FILE="/etc/tor/torrc"

        echo "DataDirectory $DATA_DIR" > $FILE
        echo "RunAsDaemon 1" >> $FILE
        echo "ShutdownWaitLength 0" >> $FILE
        echo "" >> $FILE  # new line
        echo "TestingTorNetwork 1" >> $FILE

        DIR_NICKNAME=$(echo $TOR_DIR | sed 's/-//g')
        echo "DirAuthority $DIR_NICKNAME no-v2 v3ident=$AUTH_CERT orport=5000 $AUTH_IP:7000 $AUTH_FINGERPRINT" >> $FILE

        echo "" >> $FILE  # new line

        if [ "$TOR_LOG" = "true" ]; then
            echo "SafeLogging 0" >> $FILE
            echo "Log notice file $LOG_DIR/tor-notice.log" >> $FILE
            echo "Log info file $LOG_DIR/tor-info.log" >> $FILE
            echo "Log debug file $LOG_DIR/tor-debug.log" >> $FILE
            echo "" >> $FILE  # new line
        fi

        TOR_NICKNAME=$(echo $HOSTNAME | sed 's/-//g')
        echo "Nickname $TOR_NICKNAME" >> $FILE

        echo "Address $IP" >> $FILE
        echo "ContactInfo $HOSTNAME@ewu.edu" >> $FILE
        echo "" >> $FILE  # new line
        echo "SocksPort 0  # disable client" >> $FILE
        echo "ControlPort 9051  # enable nyx" >> $FILE
        echo "" >> $FILE  # new line

        if [ "$TOR_BRIDGE" != "" ]; then
            while ! [ -f "logs/$TOR_BRIDGE/ready" ]; do
                echo "waiting for logs/$TOR_BRIDGE/ready"
                sleep 3  # seconds
            done

            BRIDGE_IP="$(cat logs/$TOR_BRIDGE/ip)"
            BRIDGE_FINGERPRINT="$(cat logs/$TOR_BRIDGE/fingerprint)"

            echo "UseBridges 1" >> $FILE
            echo "Bridge $BRIDGE_IP:5000 $BRIDGE_FINGERPRINT" >> $FILE
        fi

        echo "" >> $FILE  # new line
        echo "# Hidden Service - uses Tor for encryption not HTTPS" >> $FILE
        echo "HiddenServiceDir $DATA_DIR/www" >> $FILE
        echo "HiddenServicePort 80 127.0.0.1:80" >> $FILE
    done

    tor

    # wait for hostname
    while ! [ -f "$DATA_DIR/www/hostname" ]; do
        echo "waiting for hostname"
        sleep 3  # seconds
    done

    cp $DATA_DIR/www/hostname logs/$HOSTNAME/hostname
fi

# Useful tor commands:
#   Circuit information: `nyx`
#   Request from server: `$TOR_CURL <Server IP>/<Page>`
#   Request from hidden server: `$TOR_CURL <Server Hostname>/<Page>`
#       - The `hostname` can be found at: `logs/${SERVER}/hostname`

# create index
FILE="/app/www/index.html"
echo "<html>" > $FILE
echo "" >> $FILE  # new line
echo "<head>" >> $FILE
echo -e "\t<title>$HOSTNAME</title>" >> $FILE
echo "</head>" >> $FILE
echo "" >> $FILE  # new line
echo "<body>" >> $FILE
echo -e "\t<p>Server up... </p>" >> $FILE
echo "</body>" >> $FILE
echo "" >> $FILE  # new line
echo "</html>" >> $FILE

# setup nginx
FILE="/etc/nginx/nginx.conf"

echo "include /etc/nginx/modules/*.conf;" > $FILE
echo "include /etc/nginx/conf.d/*.conf;" >> $FILE
echo "" >> $FILE  # new line
echo "error_log /app/logs/$HOSTNAME/nginx-error.log warn; # requires absolute path" >> $FILE
echo "" >> $FILE  # new line
echo "worker_processes auto;" >> $FILE
echo "events {" >> $FILE
echo -e "\tworker_connections 1024;" >> $FILE
echo "}" >> $FILE
echo "" >> $FILE  # new line
echo "http {" >> $FILE
echo -e "\t# Includes mapping of file name extensions to MIME types of responses" >> $FILE
echo -e "\t# and defines the default type." >> $FILE
echo -e "\tinclude /etc/nginx/mime.types;" >> $FILE
echo -e "\tdefault_type application/octet-stream;" >> $FILE
echo "" >> $FILE  # new line
echo -e "\t# Don't tell nginx version to the clients." >> $FILE
echo -e "\tserver_tokens off; # Default is 'on'." >> $FILE
echo "" >> $FILE  # new line
echo -e "\t# Sendfile copies data between one FD and other from within the kernel," >> $FILE
echo -e "\t# which is more efficient than read() + write()." >> $FILE
echo -e "\tsendfile on; # Default is off." >> $FILE
echo "" >> $FILE  # new line
echo -e "\t# Causes nginx to attempt to send its HTTP response head in one packet," >> $FILE
echo -e "\t# instead of using partial frames." >> $FILE
echo -e "\ttcp_nopush on; # Default is 'off'." >> $FILE
echo "" >> $FILE  # new line
echo -e "\tssl_protocols TLSv1.2 TLSv1.3;" >> $FILE
echo "" >> $FILE  # new line
echo -e "\t# Specifies that our cipher suits should be preferred over client ciphers." >> $FILE
echo -e "\tssl_prefer_server_ciphers on; # Default is 'off'." >> $FILE
echo "" >> $FILE  # new line
echo -e "\t# Enables a shared SSL cache with size that can hold around 8000 sessions." >> $FILE
echo -e "\tssl_session_cache shared:SSL:2m; # Default is 'none'." >> $FILE
echo "" >> $FILE  # new line
echo -e "\t# Specifies a time during which a client may reuse the session parameters." >> $FILE
echo -e "\tssl_session_timeout 20m; # Default is '5m'." >> $FILE
echo "" >> $FILE  # new line
echo -e "\t# Disable TLS session tickets (they are insecure)." >> $FILE
echo -e "\tssl_session_tickets off; # Default is 'on'." >> $FILE
echo "" >> $FILE  # new line
echo -e "\t# Enables gzip compression if requested by client." >> $FILE
echo -e "\tgzip on; # Default is 'off'." >> $FILE
echo "" >> $FILE  # new line
echo -e "\t# Set the Vary HTTP header as defined in the RFC 2616." >> $FILE
echo -e "\tgzip_vary on; # Default is 'off'." >> $FILE
echo "" >> $FILE  # new line

if [ "$QUERY_LOG" = "true" ]; then
    echo -e "\t# Specifies the main log format." >> $FILE
    echo -e "\tlog_format main '\$remote_addr - \$remote_user [\$time_local] \"\$request\" '" >> $FILE
    echo -e "\t\t\t'\$status \$body_bytes_sent \"\$http_referer\" '" >> $FILE
    echo -e "\t\t\t'\"\$http_user_agent\" \"\$http_x_forwarded_for\"';" >> $FILE
    echo "" >> $FILE  # new line
    echo -e "\t# Sets the path, format, and configuration for a buffered log write." >> $FILE
    echo -e "\taccess_log /app/logs/$HOSTNAME/nginx-access.log main; # requires absolute path" >> $FILE
else
    echo -e "\taccess_log off;"
fi

echo "" >> $FILE  # new line
echo -e "\t# Includes virtual hosts configs." >> $FILE
echo -e "\tinclude /etc/nginx/http.d/*.conf;" >> $FILE
echo "}" >> $FILE

# setup server
FILE="/etc/nginx/http.d/default.conf"

echo "server {" > $FILE
echo -e "\t# HTTP" >> $FILE
echo -e "\tlisten 80 default_server;" >> $FILE
echo "" >> $FILE  # new line
echo -e "\t# HTTPS" >> $FILE
echo -e "\tlisten 443 ssl default_server;" >> $FILE
echo "" >> $FILE  # new line
echo -e "\tssl_certificate /app/ssl/public.crt;" >> $FILE
echo -e "\tssl_certificate_key /app/ssl/private.key;" >> $FILE
echo "" >> $FILE  # new line
echo -e "\t# Pages" >> $FILE
echo -e "\troot /app/www;" >> $FILE
echo -e "\tindex index.html;" >> $FILE
echo "" >> $FILE  # new line
echo -e "\tkeepalive_timeout 60;" >> $FILE
echo "" >> $FILE  # new line
echo -e "\tlocation / {" >> $FILE
echo -e "\t\t# First attempt to serve request as file, then" >> $FILE
echo -e "\t\t# as directory, then fall back to displaying a 404." >> $FILE
echo -e "\t\ttry_files \$uri \$uri/ =404;" >> $FILE
echo -e "\t}" >> $FILE
echo "}" >> $FILE

# run
trap "exit 0" SIGTERM

if [ "$AUTO_RESTART" = "true" ]; then
    nginx -g 'daemon off;' &
else
    nginx
    sleep infinity &
fi

wait $!
