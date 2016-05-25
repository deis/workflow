# Upgrading Workflow

To upgrade to a newer version of Workflow, run the following:

```
$ helmc uninstall workflow-beta3 -n deis
$ helmc fetch deis/workflow-beta4
$ helmc generate -x manifests workflow-beta4
$ cp `helmc home`/workspace/charts/workflow-beta3/manifests/deis-database-secret-creds.yaml \
    `helmc home`/workspace/charts/workflow-beta4/manifests/
$ helmc install workflow-beta4
```

Make sure to copy the existing `deis-database-secret-creds.yaml` manifest into the new chart
location *after* `helmc generate` to keep database credentials intact.

## Off-Cluster Storage Required

A Workflow upgrade requires using off-cluster object storage, since the default
in-cluster storage is ephemeral. Upgrading Workflow with the in-cluster default
of [Minio][] will result in data loss.

See [Configuring Object Storage][] to learn how to store your Workflow data off-cluster.

## Keeping Essential Pieces

!!! note
    "Keeper" upgrade behavior requires Helm Classic 0.8.0 or newer and the workflow-rc1
    or workflow-dev chart.

Helm Classic recognizes when a manifest inside a chart is marked as a "keeper" and will leave
it alone during `helmc uninstall`.

The Workflow Chart marks the "deis" Kubernetes `Namespace` and the `Service` for the registry
and for the router as keepers. This keeps the external `LoadBalancer` intact so that routing
and DNS are preserved while reinstalling Workflow.

To remove Workflow completely from a Kubernetes cluster, run the following:

```
$ helmc uninstall -n deis -y workflow-dev
$ kubectl delete ns deis  # Be sure you want to delete the
                          # Namespace and all its contents!
```

See the Helm Classic documentation for more detail about [keeper manifests].

[configuring object storage]: ../installing-workflow/configuring-object-storage.md
[keeper manifests]: http://helm-classic.readthedocs.io/en/latest/awesome/#keeper-manifests
[minio]: https://github.com/deis/minio
