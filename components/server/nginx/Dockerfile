FROM alpine:latest
RUN apk upgrade --no-cache

# additional tools

RUN apk add curl tcpdump net-tools bind-tools
RUN apk add iptables iputils busybox-extras

# setup nginx

RUN apk add nginx

WORKDIR /app

COPY ./ssl ./ssl
COPY ./www ./www

COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./default.conf /etc/nginx/http.d/default.conf

# typically utilities, such as apk, are removed and the user is changed from sudo
# for convenience, I am doing neither

RUN mkdir ./shared

# expose ports

EXPOSE 80/tcp
EXPOSE 443/tcp

# run nginx in foreground

COPY ./startup.sh .
RUN chmod +x ./startup.sh

CMD ["./startup.sh"]
