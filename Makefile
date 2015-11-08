ifndef BUILD_TAG
  BUILD_TAG = git-$(shell git rev-parse --short HEAD)
endif

COMPONENT = workflow
IMAGE = $(IMAGE_PREFIX)$(COMPONENT):$(BUILD_TAG)
SHELL_SCRIPTS = $(wildcard rootfs/bin/*) $(shell find "rootfs" -name '*.sh')

check-docker:
	@if [ -z $$(which docker) ]; then \
	  echo "Missing \`docker\` client which is required for development"; \
	  exit 2; \
	fi

build: docker-build

docker-build: check-docker
	docker build --rm -t $(IMAGE) rootfs

docker-push:
	docker push ${IMAGE}

clean: check-docker
	docker rmi $(IMAGE)

commit-hook:
	cp contrib/util/commit-msg .git/hooks/commit-msg

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
	venv/bin/pip install --disable-pip-version-check -q -r rootfs/requirements.txt -r rootfs/dev_requirements.txt

test: test-style test-unit

test-unit:
	cd rootfs \
		&& coverage run manage.py test --noinput web registry api \
		&& coverage report -m

test-style:
	cd rootfs && flake8 --show-pep8 --show-source
	shellcheck $(SHELL_SCRIPTS)

.PHONY: build clean commit-hook full-clean postgres setup-venv test test-unit test-style
