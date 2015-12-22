# If DEIS_REGISTRY is not set, try to populate it from legacy DEV_REGISTRY
DEIS_REGISTRY ?= $(DEV_REGISTRY)
IMAGE_PREFIX ?= deis
COMPONENT ?= workflow
VERSION ?= git-$(shell git rev-parse --short HEAD)
IMAGE = $(DEIS_REGISTRY)$(IMAGE_PREFIX)/$(COMPONENT):$(VERSION)
SHELL_SCRIPTS = $(wildcard rootfs/bin/*) $(shell find "rootfs" -name '*.sh') $(wildcard _scripts/*.sh)

info:
	@echo "Build tag:  ${VERSION}"
	@echo "Registry:   ${DEIS_REGISTRY}"
	@echo "Image:      ${IMAGE}"

check-docker:
	@if [ -z $$(which docker) ]; then \
	  echo "Missing \`docker\` client which is required for development"; \
	  exit 2; \
	fi

prep-bintray-json:
# TRAVIS_TAG is set to the tag name if the build is a tag
ifdef TRAVIS_TAG
	@jq '.version.name |= "$(VERSION)"' _scripts/ci/bintray-template.json | \
		jq '.package.repo |= "deis"' > _scripts/ci/bintray-ci.json
else
	@jq '.version.name |= "$(VERSION)"' _scripts/ci/bintray-template.json \
		> _scripts/ci/bintray-ci.json
endif

build: docker-build

docker-build: check-docker
	docker build --rm -t $(IMAGE) rootfs

docker-push: update-manifests
	docker push ${IMAGE}

kube-delete:
	-kubectl delete service deis-workflow
	-kubectl delete rc deis-workflow

kube-delete-database:
	-kubectl delete service deis-database
	-kubectl delete rc deis-database

kube-delete-all: kube-delete kube-delete-database

kube-create:
	kubectl create -f manifests/deis-workflow-rc.tmp.yml
	kubectl create -f manifests/deis-workflow-service.yml

kube-create-database:
	kubectl create -f manifests/deis-database-rc.yml
	kubectl create -f manifests/deis-database-service.yml

kube-create-all: kube-create-database kube-create

update-manifests:
	sed 's#\(image:\) .*#\1 $(IMAGE)#' manifests/deis-workflow-rc.yml \
		> manifests/deis-workflow-rc.tmp.yml

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

test: test-style test-unit test-functional

test-style:
	cd rootfs && flake8 --show-pep8 --show-source
	shellcheck $(SHELL_SCRIPTS)

test-unit:
	cd rootfs \
		&& coverage run manage.py test --noinput web registry api \
		&& coverage report -m

test-functional:
	@echo "Implement functional tests in _tests directory"

test-integration:
	$(MAKE) -C _tests/ test-setup test-integration

.PHONY: build clean commit-hook full-clean postgres setup-venv test test-style test-unit test-functional
