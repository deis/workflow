# Install Deis Workflow on Azure Container Service

## Check Your Setup

First check that the `helm` command is available and the version is v2.0.0 or newer.

```
$ helm version
Client: &version.Version{SemVer:"v2.0.0", GitCommit:"51bdad42756dfaf3234f53ef3d3cb6bcd94144c2", GitTreeState:"clean"}
Server: &version.Version{SemVer:"v2.0.0", GitCommit:"51bdad42756dfaf3234f53ef3d3cb6bcd94144c2", GitTreeState:"clean"}
```

Finally, intialize Helm:
```
helm init
```

Ensure the `kubectl` client is installed and can connect to your Kubernetes cluster.

## Add the Deis Chart Repository

The Deis Chart Repository contains everything needed to install Deis Workflow onto a Kubernetes cluster, with a single `helm install deis/workflow --namespace deis` command.

Add this repository to Helm:

```
$ helm repo add deis https://charts.deis.com/workflow
```

## Create New Azure Storage Account

It is recommended to have a storage account for the operational aspects of running DEIS (i.e. holding images, Disaster Recovery, Backup).  This storage account can be passed as parameters during the helm install on the next step.  Replace the SA_NAME variable with a unique name for your storage account and execute these commands.
```
$ export SA_NAME=YourGlobalUniqueName
$ az storage account create -n $SA_NAME -l $DC_LOCATION -g $RG_NAME --sku Premium_LRS
$ export SA_KEY=`az storage account keys list -n $SA_NAME -g RG_NAME --query keys[0].value --output tsv`

```

## Install Deis Workflow

Now that Helm is installed and the repository has been added, install Workflow by running:

```
$ helm install deis/workflow --namespace=deis --set controller.docker_tag=v2.9.0-acs,controller.org=kmala,global.storage=azure,azure.accountname=$SA_NAME,azure.accountkey=$SA_KEY,azure.registry_container=registry,azure.database_container=database,azure.builder_container=builder
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

Next, [configure dns](dns.md) so you can register your first user and deploy an application.

