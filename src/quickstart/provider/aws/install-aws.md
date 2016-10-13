# Installing Deis Workflow

## Check Your Setup

First check that the `helmc` command is available and the version is 0.8 or newer.

```
$ helmc --version
helmc version 0.8.1+a9c55cf
```

Ensure the `kubectl` client is installed and can connect to your Kubernetes cluster. `helmc` will
use it to communicate. You can test that it is working properly by running:

```
$ helmc target
Kubernetes master is running at https://52.9.206.49
Elasticsearch is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/elasticsearch-logging
Heapster is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/heapster
Kibana is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/kibana-logging
KubeDNS is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/kube-dns
kubernetes-dashboard is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/kubernetes-dashboard
Grafana is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/monitoring-grafana
InfluxDB is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/monitoring-influxdb
```

If you see a list of targets like the one above, `helmc` can communicate with the Kubernetes master.

## Add the Deis Chart Repository

The [Deis Chart Repository](https://github.com/deis/charts) contains everything you
need to install Deis onto your Kubernetes cluster, with a single `helmc install` command.

Run the following command to add this repository to Helm Classic:

```
$ helmc repo add deis https://github.com/deis/charts
```

!!! note
   You need [git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) installed in order to run the command above

## Install Deis Workflow

Now that you have Helm Classic installed and have added the Deis Chart Repository, install Workflow by running:

```
$ helmc fetch deis/workflow-v2.7.0            # fetches the chart into a
                                              # local workspace
$ helmc generate -x manifests workflow-v2.7.0 # generates various secrets
$ helmc install workflow-v2.7.0               # injects resources into
                                              # your cluster
```

Helm Classic will install a variety of Kubernetes resources in the `deis` namespace.
You'll need to wait for the pods that it launched to be ready. Monitor their status
by running:

```
$ kubectl --namespace=deis get pods
```

If you would like `kubectl` to automatically update as the pod states change, run (type Ctrl-C to stop the watch):
```
$ kubectl --namespace=deis get pods -w
```

Depending on the order in which the Workflow components initialize, some pods may restart. This is common during the
installation: if a component's dependencies are not yet available, that component will exit and Kubernetes will
automatically restart it.

Here, you can see that controller, builder and registry all took a few loops before there were able to start:
```
$ kubectl --namespace=deis get pods
NAME                          READY     STATUS    RESTARTS   AGE
deis-builder-hy3xv            1/1       Running   5          5m
deis-controller-g3cu8         1/1       Running   5          5m
deis-database-rad1o           1/1       Running   0          5m
deis-logger-fluentd-1v8uk     1/1       Running   0          5m
deis-logger-fluentd-esm60     1/1       Running   0          5m
deis-logger-sm8b3             1/1       Running   0          5m
deis-minio-4ww3t              1/1       Running   0          5m
deis-registry-asozo           1/1       Running   1          5m
deis-router-k1ond             1/1       Running   0          5m
deis-workflow-manager-68nu6   1/1       Running   0          5m
```

Once you see all of the pods in the `READY` state, Deis Workflow is up and running!

## Configure your AWS Load Balancer

After installing Workflow on your cluster, you will need to adjust your load balancer configuration.
By default, the connection timeout for Elastic Load Blancers is 60 seconds. Unfortunately, this timeout is too short for
long running connections when using `git push` functionality of Deis Workflow.

Deis Workflow will automatically provision and attach a Elastic Loadbalancer to the router copmonent. This
component is responsible for routing HTTP and HTTPS requests from the public internet to applications that are deployed
and managed by Deis Workflow.

By describing the `deis-router` service, you can see what IP hostname has been allocated by AWS for your Deis Workflow
cluster:

```
$ kubectl --namespace=deis describe svc deis-router | egrep LoadBalancer
Type:                   LoadBalancer
LoadBalancer Ingress:   abce0d48217d311e69a470643b4d9062-2074277678.us-west-1.elb.amazonaws.com
```

The AWS name for the ELB is the first part of hostname, before the `-`. List all of your ELBs by name to confirm:
```
$ aws elb describe-load-balancers --query 'LoadBalancerDescriptions[*].LoadBalancerName'
abce0d48217d311e69a470643b4d9062
```

Set the connection timeout to 1200 seconds, make sure you use your load balancer name:
```
$ aws elb modify-load-balancer-attributes \
        --load-balancer-name abce0d48217d311e69a470643b4d9062 \
        --load-balancer-attributes "{\"ConnectionSettings\":{\"IdleTimeout\":1200}}"
abce0d48217d311e69a470643b4d9062
CONNECTIONSETTINGS	1200
```

Next, [configure dns](dns.md) so you can register your first user and deploy an application.
