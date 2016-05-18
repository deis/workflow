# Upgrading Workflow

To upgrade to a newer version of Workflow, run the following:

```
$ helmc uninstall workflow-beta2 -n deis
$ helmc update
$ helmc fetch deis/workflow-beta4
$ helmc generate -x manifests workflow-beta4
$ helmc install workflow-beta4
```
