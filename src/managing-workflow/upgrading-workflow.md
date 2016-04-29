# Upgrading Workflow

To upgrade to a newer version of Workflow, run the following:

```
$ helm uninstall workflow-beta2 -n deis
$ helm update
$ helm fetch deis/workflow-beta3
$ helm generate -x manifests workflow-beta3
$ helm install workflow-beta3
```
