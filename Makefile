
SHELL := /bin/bash
PYTHON ?= python3

CONFIG ?= main.py


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
	echo -e "\t- configs  # list available configurations"
	echo -e "\t- graph    # create network graph"
	echo -e "\t- stats"

	echo "" # New line

	echo "Notes:"
	echo -e "\t- Compose specific config: 'make config CONFIG=NAME'"

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

up: config
	docker compose up -d

down:
	if [ -f "docker-compose.yml" ]; then
		# docker compose down may fail; this is not considered an error
		docker compose down 2> /dev/null || \
			echo "warning: Docker compose down failed."
	else
		echo "info: No docker compose file found."
	fi

# down depends upon the docker-compose file
# before we generate a new configuration, we must bring down the current network

config: down
	# may be undesired
	# remove output from previous runs
	rm -f shared/*.csv || true
	rm -f shared/*.pcap || true
	
	mkdir -p shared
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
	rm -f shared/*.csv || true
	rm -f shared/*.pcap || true
	rm -r ${CERTS_SERVER}
	
	docker container stop $$(docker container ls -a -q)
	docker image rm $$(docker image ls -a -q)
	docker system prune -f
