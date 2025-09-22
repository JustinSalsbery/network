
FROM alpine:latest
RUN apk upgrade --no-cache

# install dependencies

RUN apk add python3 python3-dev py3-pip

# install scapy
# for venv, use an environment variable not source

WORKDIR /app

RUN python3 -m venv venv
ENV PATH="venv/bin:$PATH"

RUN pip3 install --upgrade pip
RUN pip3 install scapy

# reduce image size

FROM alpine:latest
RUN apk upgrade --no-cache

# additional tools

RUN apk add curl tcpdump net-tools bind-tools ethtool
RUN apk add nmap iptables iproute2 iputils busybox-extras

# hping3 is only in the testing repository
RUN apk add hping3 --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing

# recreate environment

RUN apk add python3
ENV PATH="venv/bin:$PATH"

COPY --from=0 /app /app

WORKDIR /app

# typically utilities, such as apk, are removed and the user is changed from sudo
# for convenience, I am doing neither

RUN mkdir ./shared

COPY ./scripts ./scripts

COPY ./startup.sh .
RUN chmod +x ./startup.sh

CMD ["./startup.sh"]
