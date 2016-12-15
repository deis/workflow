# Installing Deis Workflow on Amazon Web Services

## Check Your Setup

First check that the `helm` command is available and the version is v2.1.0 or newer.

```
$ helm version
Client: &version.Version{SemVer:"v2.1.0", GitCommit:"b7b648456ba15d3d190bb84b36a4bc9c41067cf3", GitTreeState:"clean"}
Server: &version.Version{SemVer:"v2.1.0", GitCommit:"b7b648456ba15d3d190bb84b36a4bc9c41067cf3", GitTreeState:"clean"}
```

Ensure the `kubectl` client is installed and can connect to your Kubernetes cluster.

## Add the Deis Chart Repository

The Deis Chart Repository contains everything you need to install Workflow onto your Kubernetes
cluster, with a single `helm install deis/workflow --namespace deis` command.

Run the following command to add this repository to Helm:

```
$ helm repo add deis https://charts.deis.com/workflow
```

## Install Deis Workflow

Now that Helm is installed and the repository has been added, install Workflow by running:

```
$ helm install deis/workflow --namespace deis
```

Helm will install a variety of Kubernetes resources in the `deis` namespace.
Wait for the pods that Helm launched to be ready. Monitor their status by running:

```
$ kubectl --namespace=deis get pods
```

If it's preferred to have `kubectl` automatically update as the pod states change, run (type Ctrl-C to stop the watch):

```
$ kubectl --namespace=deis get pods -w
```

Depending on the order in which the Workflow components initialize, some pods may restart. This is common during the
installation: if a component's dependencies are not yet available, that component will exit and Kubernetes will
automatically restart it.

Here, it can be seen that the controller, builder and registry all took a few loops before they were able to start:

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

Once all of the pods are in the `READY` state, Deis Workflow is up and running!

## Configure your AWS Load Balancer

After installing Workflow on your cluster, you will need to adjust your load balancer
configuration. By default, the connection timeout for Elastic Load Blancers is 60 seconds.
Unfortunately, this timeout is too short for long running connections when using `git push`
functionality of Deis Workflow.

Deis Workflow will automatically provision and attach a Elastic Loadbalancer to the router
component. This component is responsible for routing HTTP and HTTPS requests from the public
internet to applications that are deployed and managed by Deis Workflow.

By describing the `deis-router` service, you can see what IP hostname has been allocated by AWS for
your Deis Workflow cluster:

```
$ kubectl --namespace=deis describe svc deis-router | egrep LoadBalancer
Type:                   LoadBalancer
LoadBalancer Ingress:   abce0d48217d311e69a470643b4d9062-2074277678.us-west-1.elb.amazonaws.com
```

The AWS name for the ELB is the first part of hostname, before the `-`. List all of your ELBs by
name to confirm:

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
