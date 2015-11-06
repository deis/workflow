include ../includes.mk

COMPONENT = controller
IMAGE = $(IMAGE_PREFIX)$(COMPONENT):$(BUILD_TAG)
SHELL_SCRIPTS = $(wildcard bin/*) $(shell find "." -name '*.sh')

build: check-docker
	docker build -t $(IMAGE) .

clean: check-docker
	docker rmi $(IMAGE)

full-clean: check-docker
	docker images -q $(IMAGE_PREFIX)$(COMPONENT) | xargs docker rmi -f

postgres:
	docker start postgres || docker run --restart="always" -d -p 5432:5432 --name postgres postgres:9.3
	docker exec postgres createdb -U postgres deis 2>/dev/null || true
	@echo "To use postgres for local development:"
	@echo "    export PGHOST=`docker-machine ip $$(docker-machine active) 2>/dev/null || echo 127.0.0.1`"
	@echo "    export PGPORT=5432"
	@echo "    export PGUSER=postgres"

setup-venv:
	@if [ ! -d venv ]; then virtualenv venv; fi
	venv/bin/pip install --disable-pip-version-check -q -r requirements.txt -r dev_requirements.txt

test: test-style test-unit

test-style:
	flake8 --show-pep8 --show-source
	shellcheck $(SHELL_SCRIPTS)

test-unit:
	coverage run manage.py test --noinput web registry api
	coverage report -m

.PHONY: build clean full-clean postgres setup-venv test test-style test-unit
