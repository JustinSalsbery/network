
SHELL := /bin/bash
PYTHON ?= python3

NETWORK ?= example-1.py


.ONESHELL:
.SILENT:

options help:
	echo "Options:"
	echo -e "\t- build"
	echo -e "\t- up"
	echo -e "\t- down"
	echo -e "\t- stats"
	echo -e "\t- clean"

CERTS := components/server/nginx/ssl
certs:
	mkdir ${CERTS} 2> /dev/null
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ${CERTS}/private.key -out ${CERTS}/public.crt \
		-subj "/C=US/ST=Washington/L=Spokane/O=Eastern Washington University/OU=Department of Computer Science/CN=Nil" 2> /dev/null

build image: certs
	FILES=$$(find components -name "Dockerfile")
	for FILE in $$FILES; do
		NAME=$$(basename $$(dirname $$FILE))
		docker build -t $$NAME $$(dirname $$FILE)
	done

compose up:
	# may be undesired
	# remove output from previous runs
	rm shared/*.csv -f || true

	# cd scripts/network
	
	# ${PYTHON} ${NETWORK}
	docker compose up -d

decompose down:
	docker compose down

stats monitor:
	echo "Exit with ctrl + c ..."
	${PYTHON} scripts/stats/main.py

clean reset:
	rm shared/*.csv -f || true
	
	docker container stop $$(docker container ls -a -q)
	docker image rm $$(docker image ls -a -q)
	docker system prune -f
