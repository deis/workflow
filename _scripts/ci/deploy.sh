#!/bin/bash

docker login -e="$DOCKER_EMAIL" -u="$DOCKER_USERNAME" -p="$DOCKER_PASSWORD"
docker push deis/workflow:latest
docker tag deis/workflow:latest quay.io/deis/workflow:latest
docker login -e="$QUAY_EMAIL" -u="$QUAY_USERNAME" -p="$QUAY_PASSWORD" quay.io
docker push quay.io/deis/workflow:latest
