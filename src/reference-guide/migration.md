# Migrating from Deis v1

Workflow uses [`kubectl`][kubectl] and [`helmc`][helmc] to manage the cluster. These tools
are equivalent to Deis v1's [`fleetctl`][fleetctl] and [`deisctl`][deisctl]. These two tools are
used for managing the cluster's state, installing the platform and inspecting its state.

This document is a "cheat sheet" for users migrating from Deis v1 to Workflow (v2). It lists most of
the known commands administrators would use with `deisctl` and translates their usage in Workflow.

## Listing all Components

```
# Deis v1
$ deisctl list

# Workflow
$ kubectl --namespace=deis get deployments
```

## Listing all Nodes

```
# Deis v1
$ fleetctl list-machines

# Workflow
$ kubectl get nodes
```

## Custom Configuration

```
# Deis v1
$ deisctl config controller set registrationMode=admin_only

# Workflow
$ kubectl --namespace=deis patch deployment deis-controller -p '{"spec":{"containers":{"env":[{"name":"REGISTRATION_MODE","value":"admin_only"}]}}}'
```

## View Component Configuration

```
# Deis v1
$ deisctl config router get bodySize

# Workflow
$ kubectl --namespace=deis get deployment deis-router -o yaml
```

## Running a Command Within a Component

```
# Deis v1
$ deisctl dock router@1

# Workflow
$ kubectl get po --namespace=deis -l app=deis-router --output="jsonpath={.items[0].metadata.name}"
deis-router-1930478716-iz6oq
$ kubectl --namespace=deis exec -it deis-router-1930478716-iz6oq bash
```

## Follow the Logs for a Component

```
# Deis v1
$ fleetctl journal -f deis-builder

# Workflow
$ kubectl get po --namespace=deis -l app=deis-builder --output="jsonpath={.items[0].metadata.name}"
deis-builder-1851090495-5n0sn
$ kubectl --namespace=deis logs -f deis-builder-1851090495-5n0sn
```


[deisctl]: http://docs.deis.io/en/latest/installing_deis/install-deisctl/
[fleetctl]: https://github.com/coreos/fleet/blob/master/Documentation/using-the-client.md
[kubectl]: http://kubernetes.io/docs/user-guide/kubectl-overview/
[helmc]: https://github.com/helm/helm-classic
