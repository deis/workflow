# Configuring Postgres

Deis Workflow's controller component relies on a PostgreSQL database to store platform state.

By default, Deis Workflow ships with the [database] component, which provides an in-cluster PostgreSQL database backed up to in-cluster or off-cluster [object storage]. Currently, for object storage, which is utilized by _several_ Workflow components, only off-cluster solutions such as S3 or GCS are recommended in production environments. Experience has shown that many operators already opting for off-cluster object storage similarly prefer to host Postgres off-cluster as well, using Amazon RDS or similar. When excercising both options, a Workflow installation becomes entirely stateless, and is thus restored or rebuilt with greater ease should the need ever arise.

## Provisioning off-cluster Postgres

First, provision a PostgreSQL RDBMS using the cloud provider or other infrastructure of your choice. Take care to ensure that security groups or other firewall rules will permit connectivity from your Kubernetes worker nodes, any of which may play host to the Workflow controller component.

Take note of the following:

1. The hostname or public IP of your PostgreSQL RDBMS
2. The port on which your PostgreSQL RDBMS runs-- typically 5432

Within the off-cluster RDBMS, manually provision the following:

1. A database user (take note of the username and password)
2. A database owned by that user (take note of its name)

If you are able to log into the RDBMS as a superuser or a user with appropriate permissions, this process will _typically_ look like this:

```
$ psql -h <host> -p <port> -d postgres -U <"postgres" or your own username>
> create user <deis username; typically "deis"> with password '<password>';
> create database <database name; typically "deis"> with owner <deis username>;
> \q
```

## Configuring Workflow

The Helm Classic chart for Deis Workflow can be easily configured to connect the Workflow controller component to an off-cluster PostgreSQL database.

* **Step 1:** If you haven't already fetched the Helm Classic chart, do so with `helmc fetch deis/workflow-v2.7.0`
* **Step 2:** Update database connection details either by setting the appropriate environment variables _or_ by modifying the template file `tpl/generate_params.toml`. Note that environment variables take precedence over settings in `tpl/generate_params.toml`.
    * **1.** Using environment variables:
        * Set `DATABASE_LOCATION` to `off-cluster`.
        * Set `DATABASE_HOST` to the hostname or public IP of your off-cluster PostgreSQL RDBMS.
        * Set `DATABASE_PORT` to the port listened to by your off-cluster PostgreSQL RDBMS-- typically `5432`.
        * Set `DATABASE_NAME` to the name of the database provisioned for use by Workflow's controller component-- typically `deis`.
        * Set `DATABASE_USERNAME` to the username of the database user that owns the database-- typically `deis`.
        * Set `DATABASE_PASSWORD` to the password for the database user that owns the database.
    * **2.** Using template file `tpl/generate_params.toml`:
        * Open the Helm Classic chart with `helmc edit workflow-v2.7.0` and look for the template file `tpl/generate_params.toml`
        * Update the `database_location` parameter to `off-cluster`.
        * Update the values in the `[database]` configuration section to properly reflect all connection details.
        * Save your changes.
    * Note: Whether using environment variables or `tpl/generate_params.toml`, you do not need to (and must not) base64 encode any values, as the Helm Classic chart will automatically handle encoding as necessary.
* **Step 3:** Re-generate the Helm Classic chart by running `helmc generate -x manifests workflow-v2.7.0`
* **Step 4:** Check the generated files in your `manifests` directory. You should see:
    * `deis-controller-deployment.yaml` contains relevant connection details.
    * `deis-database-secret-creds.yaml` exists and contains base64 encoded database username and password.
    * No other database-related Kubernetes resources are defined. i.e. none of `database-database-service-account.yaml`, `database-database-service.yaml`, or `database-database-deployment.yaml` exist.

You are now ready to `helmc install workflow-v2.7.0` [as usual][installing].

[database]: ../understanding-workflow/components.md#database
[object storage]: configuring-object-storage.md
[installing]: ../installing-workflow/index.md
