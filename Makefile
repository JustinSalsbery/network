
SHELL := /bin/bash
PYTHON ?= python3

NETWORK ?= example-1.py
NETWORK_DIR := scripts/network


.ONESHELL:
.SILENT:


options help:
	echo "Options:"
	echo -e "\t- build"
	echo -e "\t- up"
	echo -e "\t- down"
	echo -e "\t- stats"
	echo -e "\t- clean"
	
	echo "" # New line

	echo "Notes:"
	echo -e "\t- Compose specific network: 'make up NETWORK=NAME'"

CERTS_SERVER := components/server/nginx/ssl
certs:
	mkdir ${CERTS_SERVER} 2> /dev/null
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ${CERTS_SERVER}/private.key -out ${CERTS_SERVER}/public.crt \
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
	rm -f ${NETWORK_DIR}/shared/*.csv || true

	cd ${NETWORK_DIR}
	
	${PYTHON} ${NETWORK}
	docker compose up -d

decompose down:
	cd ${NETWORK_DIR}
	docker compose down

stats monitor:
	echo "Exit with ctrl + c ..."
	${PYTHON} scripts/stats/main.py

clean reset:
	rm -f ${NETWORK_DIR}/shared/*.csv || true
	rm -r ${CERTS_SERVER}
	
	docker container stop $$(docker container ls -a -q)
	docker image rm $$(docker image ls -a -q)
	docker system prune -f
