# Installing Deis Workflow

We will use the Helm Classic package manager for Kubernetes to install Deis Workflow onto a Kubernetes cluster. If you don't have Helm Classic installed, see [Helm Classic's own documentation][helm] for more info.

## Check Your Setup

First check that the `helmc` command is available and the version is 0.7 or newer.

```
$ helmc --version
helmc version 0.7.0+20a7ed7
```

Ensure the `kubectl` client is installed and can connect to your Kubernetes cluster. `helmc` will
use it to communicate. You can test that it is working properly by running:

```
$ helmc target
Kubernetes master is running at https://10.245.1.2
Heapster is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/heapster
KubeDNS is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/kube-dns
KubeUI is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/kube-ui
Grafana is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/monitoring-grafana
InfluxDB is running at https://10.245.1.2/api/v1/proxy/namespaces/kube-system/services/monitoring-influxdb
```

If you see a list of targets like the one above, `helmc` can communicate with the Kubernetes master.

Deis Workflow requires Kubernetes 1.2 or higher. You can test that by running:

```
$ kubectl version
Client Version: version.Info{Major:"1", Minor:"2", GitVersion:"v1.2.3", GitCommit:"882d296a99218da8f6b2a340eb0e81c69e66ecc7", GitTreeState:"clean"}
Server Version: version.Info{Major:"1", Minor:"2", GitVersion:"v1.2.3", GitCommit:"882d296a99218da8f6b2a340eb0e81c69e66ecc7", GitTreeState:"clean"}
```

## Add the Deis Chart Repository

The [Deis Chart Repository](https://github.com/deis/charts) contains everything you
need to install Deis onto your Kubernetes cluster, with a single `helmc install` command.

Run the following command to add this repository to Helm Classic:

```
$ helmc repo add deis https://github.com/deis/charts
```

## Install Deis Workflow

Now that you have Helm Classic installed and have added the Deis Chart Repository, install Workflow by running:

```
$ helmc fetch deis/workflow-beta3             # fetches the chart into a
                                             # local workspace
$ helmc generate -x manifests workflow-beta3  # generates various secrets
$ helmc install workflow-beta3                # injects resources into
                                             # your cluster
```

Helm Classic will install a variety of Kubernetes resources in the `deis` namespace.
You'll need to wait for the pods that it launched to be ready. Monitor their status
by running:

```
$ kubectl get pods --namespace=deis
```

If you would like `kubectl` to automatically update as the pod states change, run (type Ctrl-C to stop the watch):
```
$ kubectl get pods --namespace=deis -w
```

Once you see all of the pods in the `READY` state, Deis Workflow is up and running!

## Configure your Load Balancer

After installing Workflow on your cluster, you'll need to [configure your load balancer][lb].
Following this step is especially important on AWS because the default idle timeout for connections
on the Elastic Load Balancer is too low for the [Builder][] to finish a `git push` operation.

Next, [configure dns][] so you can register your first user.


[builder]: ../understanding-workflow/components.md#builder-builder-slugbuilder-and-dockerbuilder
[configure dns]: ../managing-workflow/configuring-dns.md
[helm]: http://helm.sh
[lb]: ../managing-workflow/configuring-load-balancers.md
