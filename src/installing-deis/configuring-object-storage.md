# Configure Object Storage

A variety of Deis components rely on an object storage system to do their work. These components are:

- [builder](https://github.com/deis/builder)
- [slugbuilder](https://github.com/deis/slugbuilder)
- [slugrunner](https://github.com/deis/slugrunner)
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

The builder looks for the below environment variables to determine where the object storage system is. The builder looks in-order for these variables. If it finds two, the one higher in the list will be used.

- `DEIS_OUTSIDE_STORAGE` - The external S3-compatible object storage system. Commonly used URLs:
  - `s3.amazonaws.com` for Amazon S3's `us-east-1a` region
  - `storage.googleapis.com` for Google Cloud Storage
- `DEIS_MINIO_SERVICE_HOST` and `DEIS_MINIO_SERVICE_PORT` - The in-cluster Minio service. Additional notes about these variables:
  - They are set automatically by Kubernetes if you run [Minio](http://minio.io) as a service in the cluster
  - The [Helm chart for Deis](https://github.com/deis/charts/tree/master/deis-dev) installs Minio by default, so the Builder will use Minio by default.

The builder also uses an environment variable to determine the name of the bucket it should store build artifacts in. It uses `git` by default, but if your credentials (see below) don't have read and write access to it, you'll have to specify a different bucket. To do so, simply set the `BUCKET` environment variable to another value (`deis-builds`, for example).

### Credentials

The builder reads credentials from the below locations on the filesystem.

- Key: `/var/run/secrets/object/store/access-key-id`
- Secret `/var/run/secrets/object/store/access-key-secret`

### A Note on Google Cloud Storage

As you may know, Google Cloud Storage (GCS) can [interoperate with the S3 API](https://cloud.google.com/storage/docs/interoperability), and, if you choose to use Google Cloud Storage for object storage, you'll have to turn on this interoperability mode.

If you choose to use Google Cloud Storage, set your `DEIS_OUTSIDE_STORAGE` environment variable to `storage.googleapis.com`, and follow [these instructions](https://cloud.google.com/storage/docs/migrating?hl=en_US#keys) to generate an S3 compatible access key ID and access key secret. Store these credentials just as you would if they were AWS S3 or Minio credentials. As mentioned above, we recommend storing these as Kubernetes secrets. See the "Configuring Deis Components" section above for more details and examples.

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

## [deis/registry](https://github.com/deis/registry)

The registry is configured slightly differently from most of the other components. Read on for details.

### Environment Variables

The registry looks for a `REGISTRY_STORAGE` environment variable, which it then uses as a key to look up the object storage location and authentication information in a configuration file. See below for details on that file.

### Credentials

The registry reads the credential information from a `/var/run/secrets/deis/registry/creds/objectstorage-keyfile` file. See https://github.com/deis/charts/blob/master/deis-dev/tpl/deis-objectstorage-secret.yaml for an example of what that file should look like.

## [deis/database](https://github.com/deis/postgres)

The database is configured slightly differently from the other components. Read the two sections below for details.

### Environment Variables

The database looks for a `DATABASE_STORAGE` environment variable, which it then uses as a key to look up the object storage location and authentication information in a configuration file. See below for the details on that file.

## Credentials

The database reads the credentials information from a `/var/run/secrets/deis/objectstore/creds/objectstorage-keyfile` file. See https://github.com/deis/charts/blob/master/deis-dev/tpl/deis-objectstorage-secret.yaml for an example of what that file should look like.

# Limitations

Below is a list of known limitations of our components' ability to interact with object storage systems.

- [The Deis registry component](https://github.com/deis/registry) will not automatically look up the Kubernetes Minio service, nor will it look for other storage env vars. That fix is being tracked in a [GitHub issue](https://github.com/deis/registry/issues/7) and is planned for our beta release.
