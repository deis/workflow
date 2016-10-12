# Upgrading Workflow

Deis Workflow releases may be upgraded in-place with minimal downtime. This upgrade process requires:

* Helm Classic, version [0.8.0 or newer](https://github.com/helm/helm-classic/releases/tag/0.8.0)
* Configured Off-Cluster Storage
* A copy of the database and builder secrets from your running cluster
* Workflow manifests annotated with `helm-keep: true` (rc1 or later)
* A Kubernetes cluster with more than one node is required for the rolling upgrade of the deis-router (as it is a rolling upgrade with host ports)

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

See the Helm Classic documentation for more detail about [keeper manifests].

## Upgrade Process

### Step 1: Verify component annotations and prepare upgrade

To verify that the deis namespace and all the deis-* services are marked as "keepers," run a
command like this one for each component:

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

Exporting environment variables for the previous and latest versions will help reduce confusion later on:

```
$ export PREVIOUS_WORKFLOW_RELEASE=v2.6.0
$ export DESIRED_WORKFLOW_RELEASE=v2.7.0
```

### Step 2: Fetch new charts

Workflow charts are always published with a version number intact. The command `helmc update` updates the local chart
repository to the latest set of releases.

```
# update the charts repo
$ helmc update
```

Fetching the new chart copies the chart from the chart cache into the helmc workspace for customization.

```
# fetch new chart
$ helmc fetch deis/workflow-${DESIRED_WORKFLOW_RELEASE}
```

### Step 3: Fetch credentials

The first time Workflow is installed, Helm automatically generates secrets for the builder and database components.
When upgrading, take care to use credentials from the running Workflow installation. The following commands export the
secrets to the local workstation. They will be copied into place in a later step.

```
# fetch the current database credentials to the local workstation
$ kubectl --namespace=deis get secret database-creds -o yaml > ~/active-deis-database-secret-creds.yaml

# fetch the builder component ssh keys to the local workstation
$ kubectl --namespace=deis get secret builder-ssh-private-keys -o yaml > ~/active-deis-builder-secret-ssh-private-keys.yaml
```

### Step 4: Modify and update configuration

Before generating the manifests for the newest release, operators should update the new `generate_params.toml` to match
configuration from the **previous release**.

```
# update your off-cluster storage configuration
$ $EDITOR $(helmc home)/workspace/charts/workflow-${DESIRED_WORKFLOW_RELEASE}/tpl/generate_params.toml
```

```
# generate templates for the new release
$ helmc generate -x manifests workflow-${DESIRED_WORKFLOW_RELEASE}
```

### Step 5: Apply secrets

After generating new manifests in the previous step, copy the current secrets into place:

```
# copy your active database secrets into the helmc workspace for the desired version
$ cp ~/active-deis-database-secret-creds.yaml \
	$(helmc home)/workspace/charts/workflow-${DESIRED_WORKFLOW_RELEASE}/manifests/deis-database-secret-creds.yaml

# copy your active builder ssh keys into the helmc workspace for the desired version
$ cp ~/active-deis-builder-secret-ssh-private-keys.yaml \
	$(helmc home)/workspace/charts/workflow-${DESIRED_WORKFLOW_RELEASE}/manifests/deis-builder-secret-ssh-private-keys.yaml
```

!!! note
    Make sure to copy the existing credentials manifests into the new chart
    location *after* `helmc generate` to preserve credentials from the running system.

### Step 6: Apply the Workflow upgrade

Helm Classic will remove all components from the previous release that are **not** marked as keepers. As of Workflow
2.3 and later, the controller, registry and router will be left in-service. Traffic to applications deployed through
Worfklow will continue to flow between the `uninstall` and `install` commands.

If Workflow is not configured to use off-cluster Postgres the Workflow API will experience a brief period of downtime
while the database component recovers from backup.

```
# uninstall workflow
$ helmc uninstall workflow-${PREVIOUS_WORKFLOW_RELEASE} -n deis

# install latest workflow release
$ helmc install workflow-${DESIRED_WORKFLOW_RELEASE}
```

### Step 7: Verify upgrade

Verify that all components have started and passed their readiness checks:

```
$ kubectl --namespace=deis get pods
NAME                                     READY     STATUS    RESTARTS   AGE
deis-builder-2448122224-3cibz            1/1       Running   0          5m
deis-controller-1410285775-ipc34         1/1       Running   3          5m
deis-database-e7c5z                      1/1       Running   0          5m
deis-logger-cgjup                        1/1       Running   3          5m
deis-logger-fluentd-45h7j                1/1       Running   0          5m
deis-logger-fluentd-4z7lw                1/1       Running   0          5m
deis-logger-fluentd-k2wsw                1/1       Running   0          5m
deis-logger-fluentd-skdw4                1/1       Running   0          5m
deis-logger-redis-8nazu                  1/1       Running   0          5m
deis-monitor-grafana-tm266               1/1       Running   0          5m
deis-monitor-influxdb-ah8io              1/1       Running   0          5m
deis-monitor-telegraf-51zel              1/1       Running   1          5m
deis-monitor-telegraf-cdasg              1/1       Running   0          5m
deis-monitor-telegraf-hea6x              1/1       Running   0          5m
deis-monitor-telegraf-r7lsg              1/1       Running   0          5m
deis-nsqd-3yrg2                          1/1       Running   0          5m
deis-registry-1814324048-yomz5           1/1       Running   0          5m
deis-registry-proxy-4m3o4                1/1       Running   0          5m
deis-registry-proxy-no3r1                1/1       Running   0          5m
deis-registry-proxy-ou8is                1/1       Running   0          5m
deis-registry-proxy-zyajl                1/1       Running   0          5m
deis-router-1357759721-a3ard             1/1       Running   0          5m
deis-workflow-manager-2654760652-kitf9   1/1       Running   0          5m
```

[configuring object storage]: ../installing-workflow/configuring-object-storage.md
[keeper manifests]: http://helm-classic.readthedocs.io/en/latest/awesome/#keeper-manifests
[minio]: https://github.com/deis/minio

### Step 7: Upgrade the deis client

Your deis platform users should now upgrade their deis client to avoid getting `WARNING: Client and server API versions do not match. Please consider upgrading.` warnings.

```
curl -sSL http://deis.io/deis-cli/install-v2.sh | bash && sudo mv deis $(which deis)
```
