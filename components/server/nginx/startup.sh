#!/bin/sh

# setup iface
for IFACE in $IFACES; do
    SRC_IP="$(echo $SRC_IPS | cut -d' ' -f1)"  # the first index
    SRC_IPS="$(echo $SRC_IPS | cut -d' ' -f2-)"  # the rest of the list

    NET_MASK="$(echo $NET_MASKS | cut -d' ' -f1)"
    NET_MASKS="$(echo $NET_MASKS | cut -d' ' -f2-)"

    GATEWAY="$(echo $GATEWAYS | cut -d' ' -f1)"
    GATEWAYS="$(echo $GATEWAYS | cut -d' ' -f2-)"

    ifconfig $IFACE $SRC_IP netmask $NET_MASK
    if [ "$GATEWAY" != "None" ]; then
        route add default gateway $GATEWAY $IFACE
    fi
done

# run nginx in the foreground
nginx -g "daemon off;"
