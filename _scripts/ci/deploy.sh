#!/usr/bin/env bash
#
# Build and push Docker images to Docker Hub and quay.io.
#

cd "$(dirname "$0")"

docker login -e="$DOCKER_EMAIL" -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD" docker.io
REGISTRY=docker.io IMAGE_PREFIX=deisci BUILD_TAG=v2-alpha make -C ../.. docker-build docker-push
docker login -e="$QUAY_EMAIL" -u="$QUAY_USERNAME" -p="$QUAY_PASSWORD" quay.io
REGISTRY=quay.io IMAGE_PREFIX=deisci BUILD_TAG=v2-alpha make -C ../.. docker-build docker-push
