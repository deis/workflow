# Tuning Component Settings

Helm Charts are a set of Kubernetes manifests that reflect best practices for deploying an
application or service. Helm is heavily influenced by [Homebrew](http://brew.sh/), including the
[formula model](https://github.com/Homebrew/homebrew-core). A Helm Chart is to Helm as a Formula
is to Homebrew.

After you fetch the Workflow chart, you can customize the chart using `helmc edit` before using
`helmc generate` and `helmc install` to complete the installation. To customize the respective
component, edit `tpl/deis-<component>-deployment.yaml` and modify the `env` section of the component to
tune these settings.

For example, to allow only administrators to register new accounts in the controller,
edit `tpl/deis-controller-deployment.yaml` and add the following under the `env` section:

```
env:
  - name: REGISTRATION_MODE
    value: "admin_only"
```

## Setting Resource limits

You can set resource limits to Workflow components by modifying the template file `tpl/generate_params.toml`.
This file has a section for each Workflow component. To set a limit to any Workflow component just add `limits_cpu`, `limits_memory`
in the section and set them to the appropriate values.

Below is an example of how the builder section of `tpl/generate_params.toml` might look with CPU and memory limits set:

```
[builder]
org = "deisci"
pullPolicy = "Always"
dockerTag = "canary"
limits_cpu = "100m"
limits_memory = "50Mi"
```

## Customizing the Builder

The following environment variables are tunable for the [Builder][] component:

Setting | Description
------- | ---------------------------------
DEBUG   | Enable debug log output (default: false)

## Customizing the Controller

The following environment variables are tunable for the [Controller][] component:

Setting                                         | Description
----------------------------------------------- | ---------------------------------
REGISTRATION_MODE                               | set registration to "enabled", "disabled", or "admin_only" (default: "enabled")
GUNICORN_WORKERS                                | number of [gunicorn][] workers spawned to process requests (default: CPU cores * 4 + 1)
RESERVED_NAMES                                  | a comma-separated list of names which applications cannot reserve for routing (default: "deis, deis-builder, deis-workflow-manager")
SLUGRUNNER_IMAGE_NAME                           | the image used to run buildpack application slugs (default: "quay.io/deisci/slugrunner:canary")
DEIS_DEPLOY_REJECT_IF_PROCFILE_MISSING          | rejects a deploy if the previous build had a Procfile but the current deploy is missing it. A 409 is thrown in the API. Prevents accidental process types removal. (default: "false", allowed values: "true", "false")
DEIS_DEPLOY_PROCFILE_MISSING_REMOVE             | when turned on (default) any missing process type in a Procfile compared to the previous deploy is removed. When set to false will allow an empty Procfile to go through without removing missing process types, note that new images, configs and so on will get updated on all proc types.  (default: "true", allowed values: "true", "false")

### Global and per application settings

Setting                                         | Description
----------------------------------------------- | ---------------------------------
DEIS_DEPLOY_BATCHES                             | the number of pods to bring up and take down sequentially during a scale (default: number of available nodes)
DEIS_DEPLOY_TIMEOUT                             | deploy timeout in seconds per deploy batch (default: 120)
IMAGE_PULL_POLICY                               | the kubernetes [image pull policy][pull-policy] for application images (default: "IfNotPresent") (allowed values: "Always", "IfNotPresent")
KUBERNETES_DEPLOYMENTS_REVISION_HISTORY_LIMIT   | how many [revisions][kubernetes-deployment-revision] Kubernetes keeps around of a given Deployment (default: all revisions)
KUBERNETES_POD_TERMINATION_GRACE_PERIOD_SECONDS | how many seconds kubernetes waits for a pod to finish work after a SIGTERM before sending SIGKILL (default: 30)

See the [Deploying Apps][] guide for more detailed information on those.

## Customizing the Database

The following environment variables are tunable for the [Database][] component:

Setting           | Description
----------------- | ---------------------------------
BACKUP_FREQUENCY  | how often the database should perform a base backup (default: "12h")
BACKUPS_TO_RETAIN | number of base backups the backing store should retain (default: 5)

## Customizing Fluentd

The following environment variables are tunable for [Fluentd][logger]:

Setting           | Description
----------------- | ---------------------------------
SYSLOG_HOST_1     | The hostname of a remote syslog endpoint for shipping logs
SYSLOG_PORT_1     | The port of a remote syslog endpoint for shipping logs

## Customizing the Logger

The following environment variables are tunable for the [Logger][] component:

Setting           | Description
----------------- | ---------------------------------
STORAGE_ADAPTER   | How to store logs that are sent to the logger. Legal values are "file", "memory", and "redis". (default: "redis")
NUMBER_OF_LINES   | How many lines to store in the ring buffer (default: 1000)

## Customizing the Monitor

The monitor component uses [Telegraf](https://github.com/influxdata/telegraf) under the hood, and
derives most of its configuration from it. Please see
[telegraf configuration](https://github.com/influxdata/telegraf/blob/master/docs/CONFIGURATION.md)
for more information on tuning the [Monitor][] component.

## Customizing the Registry

The [Registry][] component can be tuned by following the
[deis/distribution config doc](https://github.com/deis/distribution/blob/master/docs/configuration.md).

## Customizing the Router

The majority of router settings are tunable through annotations, which allows the router to be
re-configured with zero downtime post-installation. You can find the list of annotations to tune
[here](https://github.com/deis/router#annotations).

The following environment variables are tunable for the [Router][] component:

Setting           | Description
----------------- | ---------------------------------
POD_NAMESPACE     | The pod namespace the router resides in. This is set by the [Kubernetes downward API][downward-api].

## Customizing Workflow Manager

The following environment variables are tunable for [Workflow Manager][]:

Setting                            | Description
---------------------------------- | ---------------------------------
CHECK_VERSIONS    | Enables the external version check at <https://versions.deis.com/> (default: "true")
POLL_INTERVAL_SEC | The interval when Workflow Manager performs a version check, in seconds (default: 43200, or 12 hours)
VERSIONS_API_URL  | The versions API URL (default: "<https://versions-staging.deis.com>")
DOCTOR_API_URL    | The doctor API URL (default: "<https://doctor-staging.deis.com>")
API_VERSION       | The version number Workflow Manager sends to the versions API (default: "v2")


[Deploying Apps]: ../applications/deploying-apps.md
[builder]: ../understanding-workflow/components.md#builder
[controller]: ../understanding-workflow/components.md#controller
[database]: ../understanding-workflow/components.md#database
[Deployments]: http://kubernetes.io/docs/user-guide/deployments/
[downward-api]: http://kubernetes.io/docs/user-guide/downward-api/
[gunicorn]: http://gunicorn.org/
[kubernetes-deployment-revision]: http://kubernetes.io/docs/user-guide/deployments/#revision-history-limit
[logger]: ../understanding-workflow/components.md#logger-fluentd-logger
[monitor]: ../understanding-workflow/components.md#monitor
[pull-policy]: http://kubernetes.io/docs/user-guide/images/
[registry]: ../understanding-workflow/components.md#registry
[ReplicationControllers]: http://kubernetes.io/docs/user-guide/replication-controller/
[router]: ../understanding-workflow/components.md#router
[workflow manager]: ../understanding-workflow/components.md#workflow-manager
