# Configure Object Storage

A variety of Deis components rely on an object storage system to do their work. These components are:

- [builder](https://github.com/deis/builder)
- [slugbuilder](https://github.com/deis/slugbuilder)
- [slugrunner](https://github.com/deis/slugrunner)
- [controller](https://github.com/deis/controller)
- [registry](https://github.com/deis/registry)
- [database](https://github.com/deis/postgres)

These components are flexible and can work out of the box with almost any system that is compatible with the [S3 API](http://docs.aws.amazon.com/AmazonS3/latest/API/APIRest.html).

# Minio

Additionally, Deis ships with a [Minio](http://minio.io) [component](https://github.com/deis/minio). This component runs as a Kubernetes service, and the components listed above are configured to automatically look for that service and use it as object storage if it's available.

# Configuring the Deis Components

Every Deis component that relies on object storage relies on the following two inputs for configuration:

- One or more environment variables with host and port to describe where the object storage system is
- One or more files to provide access credentials for the object storage system.
	- We suggest storing these values in [Kubernetes secrets](http://kubernetes.io/v1.1/docs/user-guide/secrets.html) and mounting them as volumes to each pod
	- See [the deis-dev chart](https://github.com/deis/charts/tree/master/deis-dev) for examples of using and mounting secrets.

The subsections herein explain how to configure these two inputs for each applicable component.

## [deis/builder](https://github.com/deis/builder)

### Environment Variables

The builder looks for the below environment variables to determine where the object storage system is.

- `DEIS_OUTSIDE_STORAGE` - The external S3-compatible object storage system. Commonly used URLs:
  - `s3.amazonaws.com` for Amazon S3's `us-east-1a` region
  - `storage.googleapis.com` for Google Cloud Storage
- `DEIS_MINIO_SERVICE_HOST` and `DEIS_MINIO_SERVICE_PORT` - The in-cluster Minio service. Additional notes about these variables:
  - They are set automatically by Kubernetes if you run [Minio](http://minio.io) as a service in the cluster
  - The [Helm chart for Deis](https://github.com/deis/charts/tree/master/deis-dev) installs Minio by default, so the Builder will use Minio by default.

Note that if the builder finds a `DEIS_OUTSIDE_STORAGE_HOST` environment variable, it will ignore `DEIS_MINIO_SERVICE_HOST` and `DEIS_MINIO_SERVICE_PORT`. This behavior means that external object storage takes precedence over Minio.

The builder also uses an environment variable to determine the name of the bucket it should store build artifacts in. It uses `git` by default, but if your credentials (see below for how credentials are configured) don't have read and write access to that bucket, you'll have to specify a different one. 

To do so, simply set the `BUCKET` environment variable to another value (`deis-builds`, for example).

### Credentials

The builder reads credentials from the below locations on the filesystem.

- Key: `/var/run/secrets/object/store/access-key-id`
- Secret `/var/run/secrets/object/store/access-key-secret`

### A Note on Google Cloud Storage

Google Cloud Storage (GCS) can interoperate with the S3 API using a feature called [interoperability](https://cloud.google.com/storage/docs/interoperability). If you choose to use GCS for object storage, you'll have to turn on this interoperability mode. In order to do so, please follow the steps at https://cloud.google.com/storage/docs/migrating?hl=en_US#migration-simple.

When you're done, please set the `DEIS_OUTSIDE_STORAGE` environment variable to `storage.googleapis.com`, and ensure the keys that you created (as part of the previous paragraph) are in the correct locations on the filesystem.

Reminder: We recommend storing these and all other credentials as Kubernetes secrets. See the "Configuring Deis Components" section above for more details and examples.

## [deis/slugbuilder](https://github.com/deis/slugbuilder)

### Environment Variables

The slugbuilder looks for the below environment variables to determine where to download code from and upload slugs to.

- `TAR_URL` - The location of the `.tar` archive (which it will build)
- `put_url` - The location this component will upload the finished slug to

### Credentials

The slugbuilder reads credentials from the below locations on the filesystem.

- Key: `/var/run/secrets/object/store/access-key-id`
- Secret `/var/run/secrets/object/store/access-key-secret`


## [deis/slugrunner](https://github.com/deis/slugrunner)

### Environment Variables

The slugrunner uses the `SLUG_URL` environment variable to determine where to download the slug (that it will run) from.

### Credentials

The slugrunner reads credentials from the below locations on the filesystem.

- Key: `/var/run/secrets/object/store/access-key-id`
- Secret: `/var/run/secrets/object/store/access-key-secret`

## [deis/controller](https://github.com/deis/controller)

When the controller needs to launch a new buildpack application or scale one up, it uses a [replication controller](http://kubernetes.io/docs/user-guide/replication-controller/). Since the slugrunner needs to download the slug to run, it needs the object storage location of the slug and the object storage credentials.

### Environment Variables

The controller needs no environment variables for object storage configuration.

### Credentials

Since the object storage location information comes from the builder, the controller only needs access to the credentials information. The controller gets this information by accessing the `minio-user` secret (even if it's not using Minio as the object storage system) directly from the Kubernetes API.

No paths need to be mounted into the pod. Simply ensure that the secret exists in your Kubernetes cluster with the correct credentials.

## [deis/registry](https://github.com/deis/registry)

The registry is configured slightly differently from most of the other components. Read on for details.

### Environment Variables

The registry looks for a `REGISTRY_STORAGE` environment variable, which it then uses as a key to look up the object storage location and authentication information in a configuration file. See below for details on that file.

### Credentials

The registry reads the credential information from a `/var/run/secrets/deis/registry/creds/objectstorage-keyfile` file. This is generated automatically (as part of the `helm generate` command) based on the configuration options given in the https://github.com/deis/charts/blob/master/deis-dev/tpl/objectstorage.toml file.

## [deis/database](https://github.com/deis/postgres)

The database is configured slightly differently from the other components. Read the two sections below for details.

### Environment Variables

The database looks for a `DATABASE_STORAGE` environment variable, which it then uses as a key to look up the object storage location and authentication information in a configuration file. See below for the details on that file.

## Credentials

The database reads the credentials information from a `/var/run/secrets/deis/objectstore/creds/objectstorage-keyfile` file. This is generated automatically during helm generate based on the configuration options given in the https://github.com/deis/charts/blob/master/deis-dev/tpl/objectstorage.toml.
