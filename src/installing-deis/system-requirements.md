# Resource Requirements

When deploying Deis, it's important to provision machines with adequate resources. Deis is a highly-available distributed system, which means that Deis components and your deployed applications will move around the cluster onto healthy hosts as hosts leave the cluster for various reasons (failures, reboots, autoscalers, etc.). Because of this, you should have ample spare resources on any machine in your cluster to withstand the additional load of running services for failed machines.

## Resources

Deis components consume approximately 2 - 2.5GB of memory across the cluster, and approximately 30GB of hard disk space. Because each machine should be able to absorb additional load should a machine fail, each machine must have:

* At least 4GB of RAM (more is better)
* At least 40GB of hard disk space

Note that these estimates are for Deis and Kubernetes only, and there should be ample room for deployed applications.

Running smaller machines will likely result in increased system load and has been known to result in component failures and other problems.


# Kubernetes Requirements

## Versions

Deis workflow has been tested with the Kubernetes v1.1 release line. While Kubernetes 1.2 may work we haven't fully tested that release.

## Daemon Sets

The logging components require Kubernetes Daemon Sets API. DaemonSets are not enabled by default in the v1.1 release line, to enable these extensions follow the instructions found [here](http://kubernetes.io/v1.1/docs/api.html#enabling-resources-in-the-extensions-group). If you are running Kubernetes v1.2, DaemonSets are enabled by default.

Specific steps to enable api extensions may vary based on your Kubernetes configuration. For example, to update a CoreOS Kubernetes cluster edit the API server unit file and add the following line to the `ExecStart` stanza: `--runtime_config=extensions/v1beta1=true,extensions/v1beta1/daemonsets=true`.

Restart your API server and check that the extensions API is enabled by running:

```
$ kubectl api-versions
extensions/v1beta1
v1
$
```

# Docker Requirements

## Docker Version

Any Kubernetes 1.1 cluster should also use a Docker version < 1.10.0 so that `kubectl exec` and Deis database health checks work properly (Refs: [fsouza/go-dockerclient#455](https://github.com/fsouza/go-dockerclient/issues/455) and [kubernetes/kubernetes#19720](https://github.com/kubernetes/kubernetes/issues/19720)).

## Docker Insecure Registry

The on-cluster, Deis managed Docker registry is not deployed with TLS by default. As such, all docker daemons on your Kubernetes worker nodes must be configured with an appropriate "insecure-registry". The subnet given to "insecure-registry" should encompase any private networks used by your hosts including the configured overlay networks. Depending on your Kubernetes configuration `10.0.0.0/8` may be sufficient.
