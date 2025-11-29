
FROM alpine:latest
RUN apk upgrade --no-cache

# additional tools

RUN apk add curl tcpdump net-tools bind-tools ethtool
RUN apk add iptables iproute2 iputils busybox-extras

# setup lb

RUN apk add bird haproxy

WORKDIR /app/

# typically utilities, such as apk, are removed and the user is changed from sudo
# for convenience, I am doing neither

RUN mkdir shared/

COPY ssl/ ssl/
COPY scripts/ scripts/

COPY startup.sh startup.sh
RUN chmod +x startup.sh

CMD ["./startup.sh"]
