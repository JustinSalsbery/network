
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

RUN apk add python3

COPY --from=0 app app

# recreate environment

WORKDIR /app

RUN mkdir shared
COPY main.py main.py

ENV PATH="venv/bin:$PATH"

# typically utilities, such as apk, are removed for security
# for convenience, I am leaving all such utilities

CMD ["venv/bin/python3", "main.py"]
