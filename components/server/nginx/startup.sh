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
        echo "error: Failed to configure ${IFACE}_0
    
    if [ "$GATEWAY" != "None" ]; then
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

# run nginx
trap "exit 0" SIGTERM
nginx -g "daemon off;" &

wait $!  # $! is the PID of nginx
