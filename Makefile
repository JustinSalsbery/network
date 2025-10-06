
SHELL := /bin/bash
PYTHON ?= python3

CONFIG ?= main.py # default configuration for network


.ONESHELL:
.SILENT:


options help:
	echo "Options:"
	echo -e "\t- build"
	echo -e "\t- up       # write docker-compose and launch"
	echo -e "\t- down"
	echo -e "\t- clean    # stops all containers and deletes all images"
	
	echo "" # New line

	echo "Helper:"
	echo -e "\t- config   # write docker-compose only"
	echo -e "\t- list     # list available configurations"
	echo -e "\t- graph    # create network graph"
	echo -e "\t- stats    # record hardware utilization"

	echo "" # New line

	echo "Notes:"
	echo -e "\t- Choose a specific config: 'make {config, up} CONFIG=NAME'"

CERTS_SERVER := components/nginx/ssl
CERTS_LB := components/haproxy/ssl
certs:
	mkdir -p ${CERTS_SERVER}
	openssl req -x509 -nodes -days 1825 -newkey rsa:2048 -keyout ${CERTS_SERVER}/private.key -out ${CERTS_SERVER}/public.crt \
		-subj "/C=US/ST=Washington/L=Spokane/O=Eastern Washington University/OU=Department of Computer Science/CN=Nil" 2> /dev/null

	mkdir -p ${CERTS_LB}
	openssl req -x509 -nodes -days 1825 -newkey rsa:2048 -keyout ${CERTS_LB}/private.key -out ${CERTS_LB}/public.crt \
		-subj "/C=US/ST=Washington/L=Spokane/O=Eastern Washington University/OU=Department of Computer Science/CN=Nil" 2> /dev/null

	# combine the public and private keys
	cat ${CERTS_LB}/public.crt ${CERTS_LB}/private.key > ${CERTS_LB}/cert.pem

build: certs
	FILES=$$(find components -name "Dockerfile")
	for FILE in $$FILES; do
		NAME=$$(basename $$(dirname $$FILE))
		docker build -t $$NAME $$(dirname $$FILE)
	done

up: config
	docker compose up -d

down:
	if [ -f "docker-compose.yml" ]; then
		docker compose down --timeout 2
	else
		echo "info: No docker compose file found."
	fi

# down depends upon the docker-compose file
# before we generate a new configuration, we must bring down the current network

config: down
	echo "(Optional) sudo rm -rf shared"
	sudo rm -rf shared || true
	
	mkdir -p shared
	${PYTHON} scripts/config/${CONFIG}

list:
	echo "Configurations:"

	CONFIGS="$$(ls scripts/config/*.py)"
	for CONFIG in $${CONFIGS}; do
		NAME="$$(basename $${CONFIG})"

		if [[ "$${NAME}" =~ ^test* ]]; then
			continue
		fi

		echo -e "\t- $${NAME}"
	done

GRAPH := shared/config-graph
GRAPH_FORMAT := png  # options: jpeg, png, pdf, svg
graph:
	if ! [ -f ${GRAPH}.gv ]; then
		echo "error: ${GRAPH}.gv not found. No network configured."
		exit 1
	fi

	neato -T${GRAPH_FORMAT} ${GRAPH}.gv -o ${GRAPH}.${GRAPH_FORMAT}
	# dot -Ksfdp produces a similar image

stats:
	echo "Exit with ctrl + c ..."
	${PYTHON} scripts/stats/main.py

clean:
	echo "(Optional) sudo rm -rf shared"
	sudo rm -rf shared || true
	
	rm -r ${CERTS_SERVER}
	rm -r ${CERTS_LB}
	
	docker container stop $$(docker container ls -a -q)
	docker image rm $$(docker image ls -a -q)
	docker system prune -f
