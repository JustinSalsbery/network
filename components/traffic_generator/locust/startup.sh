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

# setup locust
OUT="shared/locust-$HOSTNAME.csv"
FILE="locustfile.py"

echo "from locust import FastHttpUser, between, task" > $FILE
echo "class WebsiteUser(FastHttpUser):" >> $FILE
echo -e "\thost = '$PROTO://$DST_IP'" >> $FILE
echo -e "\twait_time = between($WAIT_MIN, $WAIT_MAX)" >> $FILE

i=0
for PAGE in $PAGES; do
    echo -e "\t@task" >> $FILE
    echo -e "\tdef page_$i(self):" >> $FILE
    echo -e "\t\tself.client.get('/$PAGE')" >> $FILE

    i=$((i+1))
done

# run locust
trap "pkill locust" SIGTERM
locust -f $FILE --headless -u $CONN_MAX -r $CONN_RATE --csv-full-history \
    --csv csv/results 1> /dev/null &

wait $!  # $! is the PID of locust
cp csv/results_stats_history.csv $OUT
