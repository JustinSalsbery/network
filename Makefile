
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
	echo -e "\t- clean"
	
	echo "" # New line

	echo "Helper:"
	echo -e "\t- config # write docker-compose only"
	echo -e "\t- networks # list available networks"
	echo -e "\t- stats"

	echo "" # New line

	echo "Notes:"
	echo -e "\t- Compose specific network: 'make up NETWORK=NAME'"

CERTS_SERVER := components/server/nginx/ssl
certs:
	mkdir -p ${CERTS_SERVER}
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ${CERTS_SERVER}/private.key -out ${CERTS_SERVER}/public.crt \
		-subj "/C=US/ST=Washington/L=Spokane/O=Eastern Washington University/OU=Department of Computer Science/CN=Nil" 2> /dev/null

build image: certs
	FILES=$$(find components -name "Dockerfile")
	for FILE in $$FILES; do
		NAME=$$(basename $$(dirname $$FILE))
		docker build -t $$NAME $$(dirname $$FILE)
	done

config:
	${PYTHON} scripts/network/${NETWORK}

compose up:
	# may be undesired
	# remove output from previous runs
	rm -f shared/*.csv || true

	mkdir -p shared

	${PYTHON} scripts/network/${NETWORK} || exit 1
	docker compose up -d

network networks:
	echo "Networks:"

	NETWORKS="$$(ls scripts/network/*.py)"
	for NETWORK in $${NETWORKS}; do
		NAME="$$(basename $${NETWORK})"

		if [[ "$${NAME}" =~ ^test* ]]; then
			continue
		fi

		echo -e "\t- $${NAME}"
	done

decompose down:
	docker compose down

stats monitor:
	echo "Exit with ctrl + c ..."
	${PYTHON} scripts/stats/main.py

clean reset:
	rm -f shared/*.csv || true
	rm -r ${CERTS_SERVER}
	
	docker container stop $$(docker container ls -a -q)
	docker image rm $$(docker image ls -a -q)
	docker system prune -f
