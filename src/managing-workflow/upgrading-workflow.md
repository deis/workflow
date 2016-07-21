# Upgrading Workflow

Deis Workflow releases may be upgraded in-place with minimal downtime. This upgrade process requires:

* Helm Classic, version [0.8.0 or newer](https://github.com/helm/helm-classic/releases/tag/0.8.0)
* Configured Off-Cluster Storage
* A copy of the database and builder secrets from your running cluster
* Workflow manifests annotated with `helm-keep: true` (rc1 or later)

## Off-Cluster Storage Required

A Workflow upgrade requires using off-cluster object storage, since the default
in-cluster storage is ephemeral. **Upgrading Workflow with the in-cluster default
of [Minio][] will result in data loss.**

See [Configuring Object Storage][] to learn how to store your Workflow data off-cluster.

## Keeping Essential Components

!!! note
    "Keeper" upgrade behavior requires Helm Classic 0.8.0 or newer and the workflow-v2.0.0
    or newer chart.

Helm Classic recognizes when a manifest inside a chart is marked as a "keeper"
and will not uninstall the annotated resource during `helmc uninstall`.

The Workflow Chart marks the "deis" Kubernetes `Namespace` and the `Service`
for the registry and router as keepers. This leaves the external `LoadBalancer`
intact so routing and DNS are preserved while reinstalling Workflow.

To remove Workflow completely from a Kubernetes cluster, run the following:

```
$ helmc uninstall -n deis -y workflow-v2.1.0  # or the installed Workflow version
$ kubectl delete ns deis  # Be sure you want to delete the
                          # Namespace and all its contents!
```

See the Helm Classic documentation for more detail about [keeper manifests].

## Process

To verify that the namespace, router and registry are marked as "keepers" run the following kubectl command for each component:

```
$ kubectl --namespace=deis get service deis-router \
	--output=go-template='{{ index .metadata.annotations "helm-keep" | println }}'
true
```

Manifests that are annotated correctly should return the value "true". To add a missing annotation, use `kubectl annotate`:

```
$ kubectl --namespace=deis annotate namespace deis helm-keep=true
namespace "deis" annotated
```

To upgrade to a newer version of Workflow, run the following:

```
# update the charts repo
$ helmc update

# fetch your current database credentials
$ kubectl --namespace=deis get secret database-creds -o yaml > ~/active-deis-database-secret-creds.yaml
# fetch the ssh key for the builder component
$ kubectl --namespace=deis get secret builder-ssh-private-keys -o yaml > ~/active-deis-builder-secret-ssh-private-keys.yaml

# fetch new chart
$ helmc fetch deis/workflow-v2.2.0

# update your off-cluster storage configuration
$ $EDITOR $(helmc home)/workspace/charts/workflow-v2.2.0/tpl/generate_params.toml

# generate new templates
$ helmc generate -x manifests workflow-v2.2.0

# copy your active database secrets into the helmc workspace
$ cp ~/active-deis-database-secret-creds.yaml \
	$(helmc home)/workspace/charts/workflow-v2.2.0/manifests/deis-database-secret-creds.yaml

# copy your active builder ssh keys into the helmc workspace
$ cp ~/active-deis-builder-secret-ssh-private-keys.yaml \
	$(helmc home)/workspace/charts/workflow-v2.2.0/manifests/deis-builder-secret-ssh-private-keys.yaml

# uninstall workflow
$ helmc uninstall workflow-v2.1.0 -n deis

# install workflow v2.2.0
$ helmc install workflow-v2.2.0
```

Make sure to copy the existing `deis-database-secret-creds.yaml` manifest into the new chart
location *after* `helmc generate` to keep database credentials intact.

[configuring object storage]: ../installing-workflow/configuring-object-storage.md
[keeper manifests]: http://helm-classic.readthedocs.io/en/latest/awesome/#keeper-manifests
[minio]: https://github.com/deis/minio
