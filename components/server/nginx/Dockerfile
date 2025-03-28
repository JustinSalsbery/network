FROM alpine:latest
RUN apk upgrade --no-cache

RUN apk add nginx

WORKDIR /app

# create certificate

RUN apk add openssl

RUN mkdir ./ssl
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ssl/private.key -out ssl/public.crt \
    -subj "/C=US/ST=Washington/L=Spokane/O=Eastern Washington University/OU=Department of Computer Science/CN=Nil"

RUN apk del openssl

# setup nginx

COPY ./www ./www
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./default.conf /etc/nginx/http.d/default.conf

# typically utilities, such as apk, are removed for security
# for convenience, I am leaving all such utilities

RUN mkdir ./shared

# expose ports

EXPOSE 80/tcp
EXPOSE 443/tcp

# run nginx in foreground

COPY ./startup.sh .
RUN chmod +x ./startup.sh

CMD ["./startup.sh"]
