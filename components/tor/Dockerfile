FROM alpine:latest
RUN apk upgrade --no-cache

# additional tools

RUN apk add --no-cache curl tcpdump net-tools bind-tools ethtool
RUN apk add --no-cache iptables iproute2 iputils busybox-extras

# setup tor

RUN apk add --no-cache tor nyx torsocks

WORKDIR /app/

# typically utilities, such as apk, are removed and the user is changed from sudo
# for convenience, I am doing neither

RUN mkdir shared/

COPY scripts/ scripts/

COPY startup.sh startup.sh
RUN chmod +x startup.sh

CMD ["./startup.sh"]
