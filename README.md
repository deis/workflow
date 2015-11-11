# Deis Workflow v2

[![Build Status](https://travis-ci.org/deis/workflow.svg?branch=master)](https://travis-ci.org/deis/workflow) [![Go Report Card](http://goreportcard.com/badge/deis/workflow)](http://goreportcard.com/report/deis/workflow)

Deis (pronounced DAY-iss) is an open source PaaS that makes it easy to deploy and manage applications on your own servers. Deis builds on [Kubernetes](http://kubernetes.io/) to provide a lightweight, [Heroku-inspired](http://heroku.com) workflow.

## Work in Progress

![Deis Graphic](https://s3-us-west-2.amazonaws.com/get-deis/deis-graphic-small.png)

Deis Workflow v2 is changing quickly. Your feedback and participation are more than welcome, but be aware that this project is considered a work in progress.

## Hacking Workflow

First, install [deis/etcd](https://github.com/deis/etcd) as described in its documentation. Ensure that the deis-etcd-service is running and healthy by accessing its port 4001 and seeing that the environment variable `DEIS_ETCD_1_SERVICE_HOST` is set.

One way to test this by running commands from another pod in the same namespace:

```console
$ kubectl exec alpine -- env | grep DEIS_ETCD_1_SERVICE | sort
DEIS_ETCD_1_SERVICE_HOST=10.247.187.217
DEIS_ETCD_1_SERVICE_PORT=2380
DEIS_ETCD_1_SERVICE_PORT_CLIENT=4100
DEIS_ETCD_1_SERVICE_PORT_PEER=2380
$ kubectl exec alpine -- curl -sS 10.247.187.217:4100/version
{"etcdserver":"2.2.1","etcdcluster":"2.2.0"}
```

Next build the deis/workflow image and push it to a Docker registry. The `$DEV_REGISTRY` environment variable must point to a registry accessible to your Kubernetes cluster. You may need to configure the Docker engines on your Kubernetes nodes to allow `--insecure-registry 192.168.0.0/16` (or the appropriate address range).

```console
$ make docker-build docker-push
```

Finally create a PostgreSQL database and the Deis workflow service:
```console
$ make kube-create-all
kubectl create -f manifests/deis-database-rc.yml
replicationcontrollers/deis-database
kubectl create -f manifests/deis-database-service.yml
services/deis-database
kubectl create -f manifests/deis-workflow-rc.yml.tmp
replicationcontrollers/deis-workflow
kubectl create -f manifests/deis-workflow-service.yml
services/deis-workflow
$ kubectl get pod
NAME                        READY     STATUS    RESTARTS   AGE
deis-database-34ch4         1/1       Running   0          12m
deis-etcd-1-140w7           1/1       Running   2          1h
deis-etcd-1-3jib8           1/1       Running   2          1h
deis-etcd-1-qf9ab           1/1       Running   2          1h
deis-etcd-discovery-dp2kp   1/1       Running   0          1h
deis-workflow-e8qks         1/1       Running   0          12m
$ kubectl logs deis-workflow-e8qks
+ export ETCD_PORT=4100
+ ETCD_PORT=4100
+ export ETCD_HOST=10.247.187.217
+ ETCD_HOST=10.247.187.217
...
```

## License

Copyright 2013, 2014, 2015 Engine Yard, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
