# Upgrading Workflow

To upgrade to a newer version of Workflow, run the following:

```
$ helmc uninstall workflow-beta3 -n deis
$ helmc update
$ helmc fetch deis/workflow-beta4
$ helmc generate -x manifests workflow-beta4
$ helmc install workflow-beta4
```

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

[keeper manifests]: http://helm-classic.readthedocs.io/en/latest/awesome/#keeper-manifests
