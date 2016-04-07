# Upgrading Workflow

To upgrade to a newer version of Workflow, run the following:

```
$ helm uninstall workflow-beta1 -n deis
$ helm update
$ helm fetch deis/workflow-beta2
$ helm generate -x manifests workflow-beta2
$ helm install workflow-beta2
```
