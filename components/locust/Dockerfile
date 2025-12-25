
FROM alpine:latest
RUN apk upgrade --no-cache

# install build dependencies

RUN apk add --no-cache python3 python3-dev py3-pip
RUN apk add --no-cache gcc musl-dev linux-headers

# install locust
# for venv, use an environment variable not source

WORKDIR /app/

RUN python3 -m venv venv
ENV PATH="venv/bin:$PATH"

RUN pip3 install --upgrade pip
RUN pip3 install locust

# reduce image size

FROM alpine:latest
RUN apk upgrade --no-cache

# additional tools

RUN apk add --no-cache curl tcpdump net-tools bind-tools ethtool
RUN apk add --no-cache iptables iproute2 iputils busybox-extras

# recreate environment

RUN apk add --no-cache python3
ENV PATH="venv/bin:$PATH"

COPY --from=0 /app/ /app/

WORKDIR /app/

# typically utilities, such as apk, are removed and the user is changed from sudo
# for convenience, I am doing neither

RUN mkdir logs/

COPY scripts/ scripts/

COPY startup.sh startup.sh
RUN chmod +x startup.sh

CMD ["./startup.sh"]
