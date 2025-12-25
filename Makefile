
SHELL := /bin/bash
PYTHON ?= python3


.ONESHELL:
.SILENT:


# help

.PHONY: options help
options help:
	echo "Options:"
	echo -e "\t- build"
	echo -e "\t- up            # specify config with NETWORK=<NAME>"
	echo -e "\t- down"
	echo -e "\t- test          # specify test with TEST=<NAME>"
	echo -e "\t- clean"
	
	echo "" # New line

	echo "Helper:"
	echo -e "\t- list-networks # list available networks"
	echo -e "\t- list-tests    # list available tests"
	echo -e "\t- graph         # create network graph"
	echo -e "\t- stats         # record hardware utilization"
	echo -e "\t- config        # write docker-compose only"


# network

CERTS_SERVER := components/nginx/ssl/
CERTS_LB := components/haproxy/ssl/

.PHONY: certs
certs:
	mkdir -p ${CERTS_SERVER}
	openssl req -x509 -nodes -days 1825 -newkey rsa:2048 -keyout ${CERTS_SERVER}/private.key -out ${CERTS_SERVER}/public.crt \
		-subj "/C=US/ST=Washington/L=Spokane/O=Eastern Washington University/OU=Department of Computer Science/CN=Nil" 2> /dev/null

	mkdir -p ${CERTS_LB}
	openssl req -x509 -nodes -days 1825 -newkey rsa:2048 -keyout ${CERTS_LB}/private.key -out ${CERTS_LB}/public.crt \
		-subj "/C=US/ST=Washington/L=Spokane/O=Eastern Washington University/OU=Department of Computer Science/CN=Nil" 2> /dev/null

	# combine the public and private keys
	cat ${CERTS_LB}/public.crt ${CERTS_LB}/private.key > ${CERTS_LB}/cert.pem

.PHONY: build
build: certs
	FILES=$$(find components -name "Dockerfile")
	for FILE in $$FILES; do
		NAME=$$(basename $$(dirname $$FILE))
		docker build -t $$NAME $$(dirname $$FILE)
	done

.PHONY: up
up: config
	docker compose up -d

.PHONY: down
down:
	if ! [ -f "docker-compose.yml" ]; then
		echo "info: no docker compose file found."
		exit 0
	fi

	docker compose down --timeout 2
	sudo chmod -R 777 logs/ || true

# down depends upon the docker-compose file
# before we generate a new configuration, we must bring down the current network

CONFIG ?= main.py # default configuration for network

.PHONY: config
config: down clean-logs
	mkdir -p logs/
	export PYTHONPATH="scripts/network/"
	${PYTHON} scripts/network/${NETWORK}

.PHONY: list-networks
list-networks:
	echo "Network configurations:  # run with: make up NETWORK=<NAME>"

	NETWORKS="$$(cd scripts/network; \
		find . -name '*.py' -not -path './src/*' -not -path './tests/*')"

	for NETWORK in $${NETWORKS}; do
		echo -e "\t- $${NETWORK}"
	done

GRAPH := logs/network-graph
GRAPH_FORMAT := png  # options: jpeg, png, pdf, svg

.PHONY: graph
graph:
	if ! [ -f ${GRAPH}.gv ]; then
		echo "error: ${GRAPH}.gv not found. No network configured."
		exit 1
	fi

	# dot -Ksfdp produces a similar image
	neato -T${GRAPH_FORMAT} ${GRAPH}.gv -o ${GRAPH}.${GRAPH_FORMAT}


# stats

.PHONY: stats
stats:
	sudo chmod -R 777 logs/ || true

	echo "Exit with ctrl + c ..."
	${PYTHON} scripts/stats/main.py


# test

TEST ?= example.py

.PHONY: test
test:
	${PYTHON} scripts/test/${TEST}

.PHONY: list-tests
list-tests:
	echo "Network tests:  # run with: make test TEST=<NAME>"

	TESTS="$$(cd scripts/test; \
		find . -name '*.py' -not -path './src/*')"

	for TEST in $${TESTS}; do
		echo -e "\t- $${TEST}"
	done


# clean

.PHONY: clean
clean: clean-logs clean-certs clean-docker
	rm -f docker-compose.yml

.PHONY: clean-logs
clean-logs: down
	sudo rm -rf logs/

.PHONY: clean-certs
clean-certs:
	rm -r ${CERTS_SERVER}
	rm -r ${CERTS_LB}

.PHONY: clean-docker
clean-docker: down
	docker system prune --force

.PHONY: reset-docker
reset-docker:
	docker container stop $$(docker container ls -a -q)
	docker image rm $$(docker image ls -a -q)
	docker system prune --force
