
FROM alpine:latest
RUN apk upgrade --no-cache

# install build dependencies

RUN apk add python3 python3-dev py3-pip
RUN apk add gcc musl-dev linux-headers

# install locust
# for venv, use an environment variable not source

WORKDIR /app

RUN python3 -m venv venv
ENV PATH="venv/bin:$PATH"

RUN pip3 install --upgrade pip
RUN pip3 install locust

# reduce image size

FROM alpine:latest
RUN apk upgrade --no-cache

# additional tools

RUN apk add curl tcpdump net-tools bind-tools ethtool
RUN apk add iptables iproute2 iputils busybox-extras

# recreate environment

RUN apk add python3
ENV PATH="venv/bin:$PATH"

WORKDIR /app

COPY --from=0 /app /app

# typically utilities, such as apk, are removed and the user is changed from sudo
# for convenience, I am doing neither

RUN mkdir ./shared

COPY ./startup.sh .
RUN chmod +x ./startup.sh

CMD ["./startup.sh"]
