SHELL := /bin/bash

.PHONY: run-app
run-app:
	@ source ./venv/bin/activate && ROLLUP_HTTP_SERVER_URL="http://localhost:8080/host-runner" python3.9 dapp.py

.PHONY: build
build:
	@ sunodo build

.PHONY: run
run:
	@ sunodo run

.PHONY: run-local
run-local:
	@ sunodo run --no-backend

.PHONY: test
test:
	@ ./setup_campaign.sh
