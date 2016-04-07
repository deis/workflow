# Tuning Component Settings

Helm Charts are a set of Kubernetes manifests that reflect best practices to deploy an application
or service. Helm is heavily influenced by [Homebrew](http://brew.sh/), including the
[formula model](https://github.com/Homebrew/homebrew-core). A Helm chart is to Helm as a Formula
is to Homebrew.

When you run `helmc fetch deis/workflow-beta3`, you can customize the chart with
`helmc edit workflow-beta3`. To customize the respective component, edit
`manifests/deis-<component>-rc.yaml` and modify the `env` section of the component to tune these
settings.

For example, to allow only administrators to register new accounts in the controller,
edit `manifests/deis-controller-rc.yaml` and add the following under the `env` section:

```
env:
  - name: REGISTRATION_MODE
    value: "admin_only"
```


## Customizing the Controller

The following environment variables are tunable for the [Controller][] component:

Setting             | Description
------------------- | ---------------------------------
REGISTRATION_MODE   | set registration to "enabled", "disabled", or "admin_only" (default: "enabled")
GUNICORN_WORKERS    | number of [gunicorn][] workers spawned to process requests (default: 8)
DEIS_RESERVED_NAMES | a comma-separated list of names which applications cannot reserve for routing (default: "deis")


## Customizing the Database

The following environment variables are tunable for the [Database][] component:

Setting           | Description
----------------- | ---------------------------------
BACKUP_FREQUENCY  | how ofter the database should perform a base backup (default: "12h")
BACKUPS_TO_RETAIN | number of base backups the backing store should retain (default: 5)


[controller]: ../understanding-workflow/components.md#controller
[database]: ../understanding-workflow/components.md#database
[gunicorn]: http://gunicorn.org/
