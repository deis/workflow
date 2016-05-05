# Upgrading Workflow

To upgrade to a newer version of Workflow, run the following:

```
$ helmc uninstall workflow-beta2 -n deis
$ helmc update
$ helmc fetch deis/workflow-beta3
$ helmc generate -x manifests workflow-beta3
$ helmc install workflow-beta3
```
