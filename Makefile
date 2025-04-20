
SHELL := /bin/bash
PYTHON ?= python3

CONFIG ?= main.py


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
	echo -e "\t- config  # write docker-compose only"
	echo -e "\t- configs  # list available configurations"
	echo -e "\t- stats"

	echo "" # New line

	echo "Notes:"
	echo -e "\t- Compose specific config: 'make up CONFIG=NAME'"

CERTS_SERVER := components/nginx/ssl
certs:
	mkdir -p ${CERTS_SERVER}
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ${CERTS_SERVER}/private.key -out ${CERTS_SERVER}/public.crt \
		-subj "/C=US/ST=Washington/L=Spokane/O=Eastern Washington University/OU=Department of Computer Science/CN=Nil" 2> /dev/null

build: certs
	FILES=$$(find components -name "Dockerfile")
	for FILE in $$FILES; do
		NAME=$$(basename $$(dirname $$FILE))
		docker build -t $$NAME $$(dirname $$FILE)
	done

config:
	${PYTHON} scripts/config/${CONFIG}

configs:
	echo "Configurations:"

	CONFIGS="$$(ls scripts/config/*.py)"
	for CONFIG in $${CONFIGS}; do
		NAME="$$(basename $${CONFIG})"

		if [[ "$${NAME}" =~ ^test* ]]; then
			continue
		fi

		echo -e "\t- $${NAME}"
	done

up: config
	# may be undesired
	# remove output from previous runs
	rm -f shared/*.csv || true
	mkdir -p shared

	docker compose up -d

down:
	docker compose down

stats:
	echo "Exit with ctrl + c ..."
	${PYTHON} scripts/stats/main.py

clean:
	rm -f shared/*.csv || true
	rm -r ${CERTS_SERVER}
	
	docker container stop $$(docker container ls -a -q)
	docker image rm $$(docker image ls -a -q)
	docker system prune -f
