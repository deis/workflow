# Upgrading Workflow

Deis Workflow releases may be upgraded in-place with minimal downtime. This upgrade process requires:

* Helm version [2.1.0 or newer](https://github.com/kubernetes/helm/releases/tag/v2.1.0)
* Configured Off-Cluster Storage
* A Kubernetes cluster with more than one node is required for the rolling upgrade of the deis-router (as it is a rolling upgrade with host ports)

## Off-Cluster Storage Required

A Workflow upgrade requires using off-cluster object storage, since the default
in-cluster storage is ephemeral. **Upgrading Workflow with the in-cluster default
of [Minio][] will result in data loss.**

See [Configuring Object Storage][] to learn how to store your Workflow data off-cluster.

## Upgrade Process

!!! note
    If upgrading from a [Helm Classic](https://github.com/helm/helm-classic) install, you'll need to 'migrate' the cluster to a [Kubernetes Helm](https://github.com/kubernetes/helm) installation.  See [Workflow-Migration][] for steps.

### Step 1: Apply the Workflow upgrade

Helm will remove all components from the previous release. Traffic to applications deployed through
Workflow will continue to flow during the upgrade. No service interruptions should occur.

If Workflow is not configured to use off-cluster Postgres, the Workflow API will experience a brief
period of downtime while the database recovers from backup.

First, find the name of the release helm gave to your deployment with `helm ls`, then run

```
$ helm upgrade <release-name> deis/workflow
```


**Note:** If using off-cluster object storage on [gcs](https://cloud.google.com/storage/) and/or off-cluster registry using [gcr](https://cloud.google.com/container-registry/) and intending to upgrade from a pre-`v2.10.0` chart to `v2.10.0` or greater, the `key_json` values will now need to be pre-base64-encoded.  Therefore, assuming the rest of the custom/off-cluster values are defined in the existing `values.yaml` used for previous installs, the following may be run:

```
$ B64_KEY_JSON="$(cat ~/path/to/key.json | base64 | tr -d '[:space:]')"
$ helm upgrade <release_name> deis/workflow -f values.yaml --set gcs.key_json="${B64_KEY_JSON}",registry-token-refresher.gcr.key_json="${B64_KEY_JSON}"
$ # alternatively, simply replace the appropriate values in values.yaml and do without the `--set` parameter
```

### Step 2: Verify Upgrade

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

### Step 3: Upgrade the Deis Client

Users of Deis Workflow should now upgrade their deis client to avoid getting `WARNING: Client and server API versions do not match. Please consider upgrading.` warnings.

```
curl -sSL http://deis.io/deis-cli/install-v2.sh | bash && sudo mv deis $(which deis)
```


[minio]: https://github.com/deis/minio
[Configuring Object Storage]: ../installing-workflow/configuring-object-storage.md
[Workflow-Migration]: https://github.com/deis/workflow-migration/blob/master/README.md
