# Tuning Component Settings

Helm Charts are a set of Kubernetes manifests that reflect best practices for deploying an
application or service on Kubernetes.

After you add the Deis Chart Repository, you can customize the chart using
`helm inspect values deis/workflow > values.yaml` before using `helm install` to complete the
installation.

There are a few ways to customize the respective component:

 - If the value is exposed in the `values.yaml` file as derived above, one may modify the section of the component to tune these settings.  The modified value(s) will then take effect at chart installation or release upgrade time via either of the two respective commands:

        $ helm install deis/workflow --namespace deis -f values.yaml
        $ helm upgrade deis -f values.yaml

 - If the value hasn't yet been exposed in the `values.yaml` file, one may edit the component deployment with the tuned setting.  Here we edit the `deis-controller` deployment:

        $ kubectl --namespace deis edit deployment deis-controller

    Add/edit the setting via the appropriate environment variable and value under the `env` section and save.  The updated deployment will recreate the component pod with the new/modified setting.

 - Lastly, one may also fetch and edit the chart as served by version control/the chart repository itself:

        $ helm fetch deis/workflow --untar
        $ $EDITOR workflow/charts/controller/templates/controller-deployment.yaml

    Then run `helm install ./workflow --namespace deis --name deis` to apply the changes, or `helm upgrade deis ./workflow` if the cluster is already running.

## Setting Resource limits

You can set resource limits to Workflow components by modifying the values.yaml file fetched
earlier. This file has a section for each Workflow component. To set a limit to any Workflow
component just add `limits_cpu`, `limits_memory` in the section and set them to the appropriate
values.

Below is an example of how the builder section of `values.yaml` might look with CPU and memory
limits set:

```
builder:
  org: "deisci"
  pullPolicy: "Always"
  dockerTag: "canary"
  limits_cpu: "100m"
  limits_memory: "50Mi"
```

## Customizing the Builder

The following environment variables are tunable for the [Builder][] component:

Setting                     | Description
--------------------------- | ---------------------------------
DEBUG                       | Enable debug log output (default: false)
BUILDER_POD_NODE_SELECTOR   | A node selector setting for builder job. As it may sometimes consume a lot of node resources, one may want a given builder job to run in a specific node only, so it won't affect critical nodes. for example `pool:testing,disk:magnetic`

## Customizing the Controller

The following environment variables are tunable for the [Controller][] component:

Setting                                         | Description
----------------------------------------------- | ---------------------------------
REGISTRATION_MODE                               | set registration to "enabled", "disabled", or "admin_only" (default: "admin_only")
GUNICORN_WORKERS                                | number of [gunicorn][] workers spawned to process requests (default: CPU cores * 4 + 1)
RESERVED_NAMES                                  | a comma-separated list of names which applications cannot reserve for routing (default: "deis, deis-builder, deis-workflow-manager")
SLUGRUNNER_IMAGE_NAME                           | the image used to run buildpack application slugs (default: "quay.io/deisci/slugrunner:canary")
DEIS_DEPLOY_HOOK_URLS                           | a comma-separated list of URLs to send [deploy hooks][] to.
DEIS_DEPLOY_HOOK_SECRET_KEY                     | a private key used to compute the HMAC signature for deploy hooks.
DEIS_DEPLOY_REJECT_IF_PROCFILE_MISSING          | rejects a deploy if the previous build had a Procfile but the current deploy is missing it. A 409 is thrown in the API. Prevents accidental process types removal. (default: "false", allowed values: "true", "false")
DEIS_DEPLOY_PROCFILE_MISSING_REMOVE             | when turned on (default) any missing process type in a Procfile compared to the previous deploy is removed. When set to false will allow an empty Procfile to go through without removing missing process types, note that new images, configs and so on will get updated on all proc types.  (default: "true", allowed values: "true", "false")
DEIS_DEFAULT_CONFIG_TAGS                        | set tags for all applications by default, for example: '{"role": "worker"}'. (default: '')
KUBERNETES_NAMESPACE_DEFAULT_QUOTA_SPEC         | set resource quota to application namespace by setting [ResourceQuota](http://kubernetes.io/docs/admin/resourcequota/) spec, for example: `{"spec":{"hard":{"pods":"10"}}}`, restrict app owner to spawn more then 10 pods (default: "", no quota will be applied to namespace)

### LDAP authentication settings

Configuration options for LDAP authentication are detailed [here](https://pythonhosted.org/django-auth-ldap/reference.html).

The following environment variables are available for enabling LDAP
authentication of user accounts in the [Controller][] component:

Setting            | Description
-------------------| ---------------------------------
LDAP_ENDPOINT      | The URI of the LDAP server. If not specified, LDAP authentication is not enabled (default: "", example: ```ldap://hostname```).
LDAP_BIND_DN       | The distinguished name to use when binding to the LDAP server (default: "")
LDAP_BIND_PASSWORD | The password to use with LDAP_BIND_DN (default: "")
LDAP_USER_BASEDN   | The distinguished name of the search base for user names (default: "")
LDAP_USER_FILTER   | The name of the login field in the users search base (default: "username")
LDAP_GROUP_BASEDN  | The distinguished name of the search base for user's groups names (default: "")
LDAP_GROUP_FILTER  | The filter for user's groups (default: "", example: ```objectClass=person```)

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

The following values can be changed in the `values.yaml` file or by using the `--set` flag with the Helm CLI. 

Key               | Default | Description
------------------| --------| ---------------------------------
syslog.host | "" | Host value of a syslog endpoint
syslog.port | "" | Port value of a syslog endpoint
sources.start_script | false | Capture kubernetes start script logs
sources.docker | false | Capture docker daemon logs
sources.etcd | false | Capture etcd logs
sources.kubelet | false | Capture kubelet logs
sources.kube_api | false | Capture Kubernetes API logs
sources.controller | false | Capture Kubernetes Controller logs
sources.scheduler | false | Capture Kubernetes Scheduler logs
output.disable_deis | false | Disable the Deis output plugin
boot.install_build_tools | false | Install the build tools package. This is useful when using custom plugins
daemon_environment | | Takes key-value pairs and turns them into environment variables.

For more information about the various environment variables that can be set please see the [README](https://github.com/deis/fluentd/blob/master/README.md)

## Customizing the Logger

The following environment variables are tunable for the [Logger][] component:

Setting           | Description
----------------- | ---------------------------------
STORAGE_ADAPTER   | How to store logs that are sent to the logger. Legal values are "file", "memory", and "redis". (default: "redis")
NUMBER_OF_LINES   | How many lines to store in the ring buffer (default: 1000)

## Customizing the Monitor

### [Grafana](https://grafana.com/)
We have exposed some of the more useful configuration values directly in the chart. This allows them to be set using either the `values.yaml` file or by using the `--set` flag with the Helm CLI. You can see these options below:

Setting           | Default Value  | Description
----------------- | -------------- |------------ |
user   | "admin" | The first user created in the database (this user has admin privileges)
password | "admin" | Password for the first user.
allow_sign_up | "true" | Allows users to sign up for an account.

For a list of other options you can set by using environment variables please see the [configuration file](https://github.com/deis/monitor/blob/master/grafana/rootfs/usr/share/grafana/grafana.ini.tpl) in Github.

### [Telegraf](https://docs.influxdata.com/telegraf)
For a list of configuration values that can be set by using environment variables please see the following [configuration file](https://github.com/deis/monitor/blob/master/telegraf/rootfs/config.toml.tpl).

### [InfluxDB](https://docs.influxdata.com/influxdb)
You can find a list of values that can be set using environment variables [here](https://github.com/deis/monitor/blob/master/influxdb/rootfs/home/influxdb/config.toml.tpl).

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
[deploy hooks]: deploy-hooks.md#http-post-hook
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
