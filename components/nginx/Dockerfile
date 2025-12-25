FROM alpine:latest
RUN apk upgrade --no-cache

# additional tools

RUN apk add --no-cache curl tcpdump net-tools bind-tools ethtool
RUN apk add --no-cache iptables iproute2 iputils busybox-extras
RUN apk add --no-cache tor nyx torsocks

# setup nginx

RUN apk add --no-cache nginx

WORKDIR /app/

# typically utilities, such as apk, are removed and the user is changed from sudo
# for convenience, I am doing neither

RUN mkdir logs/

COPY www/ www/
COPY ssl/ ssl/
COPY scripts/ scripts/

COPY startup.sh startup.sh
RUN chmod +x startup.sh

CMD ["./startup.sh"]
