
SHELL := /bin/bash
PYTHON ?= python3


.ONESHELL:
.SILENT:

options help:
	echo "Options:"
	echo -e "\t- build"
	echo -e "\t- up"
	echo -e "\t- down"
	echo -e "\t- stats"
	echo -e "\t- clean"

build image:
	FILES=$$(find components -name "Dockerfile")
	for FILE in $$FILES; do
		NAME=$$(basename $$(dirname $$FILE))
		docker build -t $$NAME $$(dirname $$FILE)
	done

compose up:
	# may be undesired
	# clean up csv's from previous runs
	rm shared/*.csv || true
	
	${PYTHON} scripts/network/main.py
	docker compose up -d

decompose down:
	docker compose down

stats monitor:
	echo "Exit with ctrl + c ..."
	${PYTHON} scripts/stats/main.py

clean reset:
	rm shared/*.csv || true
	
	docker container stop $$(docker container ls -a -q)
	docker image rm $$(docker image ls -a -q)
	docker system prune -f
