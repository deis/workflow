# Configuring Object Storage

A variety of Deis Workflow components rely on an object storage system to do their work including storing application slugs, Docker images and database logs.

Deis Workflow ships with [Minio][minio] by default, which provides in-cluster, ephemeral object storage. This means that _if the Minio server crashes, all data will be lost_. Therefore, **Minio should be used for development or testing only**.

## Configuring off-cluster Object Storage

Every component that relies on object storage uses two inputs for configuration:

1. Component-specific environment variables (e.g. `BUILDER_STORAGE` and `REGISTRY_STORAGE`)
2. Access credentials stored as a Kubernetes secret named `objectstorage-keyfile`

The helm chart for Deis Workflow can be easily configured to connect Workflow components to off-cluster object storage. Deis Workflow currently supports Google Compute Storage, Amazon S3 and Azure Blob Storage.

* **Step 1:** Create storage buckets for each of the Workflow subsystems: builder, registry and database
    * Note: Depending on your chosen object storage you may need to provide globally unique bucket names.
    * Note: If you provide credentials with sufficient access to the underlying storage, Workflow components will create the buckets if they do not exist.
* **Step 2:** If applicable, generate credentials that have write access to the storage buckets created in Step 1
* **Step 3:** If you haven't already fetched the helm chart, do so with `helm fetch deis/workflow-beta3`
* **Step 4:** Open the helm chart with `helm edit workflow-beta3` and look for the template file `tpl/generate_params.toml`
* **Step 5:** Update the `storage` parameter to reference the storage platform you are using: `s3`, `azure`, `gcs`
* **Step 6:** Update the values in the section which corresponds to your storage type, including region, bucket names and access credentials
    * Note: you do not need to base64 encode any of these values as Helm will handle encoding automatically
* **Step 7:** Save your changes and re-generate the helm chart by running `helm generate -x manifests workflow-beta3`
* **Step 8:** Check the generated file in your manifests directory, you should see `deis-objectstorage-secret.yaml`

You are now ready to `helm install workflow-beta3` using your desired object storage.

## Object Storage Configuration and Credentials

During the `helm generate` step, Helm creates a Kubernetes secret in the Deis namespace named `objectstorage-keyfile`. The exact structure of the file depends on storage backend specified in `tpl/generate_params.toml`.

```
# Set the storage backend
#
# Valid values are:
# - s3: Store persistent data in AWS S3 (configure in S3 section)
# - azure: Store persistent data in Azure's object storage
# - gcs: Store persistent data in Google Cloud Storage
# - minio: Store persistent data on in-cluster Minio server
storage = "minio"
```

Individual components map the master credential secret to either secret-backed environment variables or volumes. See below for the component-by-component locations.

## Component Details

### [deis/builder](https://github.com/deis/builder)

The builder looks for a `BUILDER_STORAGE` environment variable, which it then uses as a key to look up the object storage location and authentication information from the `objectstore-creds` volume.

### [deis/slugbuilder](https://github.com/deis/slugbuilder)

Slugbuilder is configured and launched by the builder component. Slugbuilder reads credential information from the standard `objectstorage-keyfile` secret.

If you are using slugbuilder as a standalone component the following configuration is important:

- `TAR_PATH` - The location of the application `.tar` archive, relative to the configured bucket for builder e.g. `home/burley-yeomanry:git-3865c987/tar`
- `PUT_PATH` - The location to upload the finished slug, relative to the configured bucket fof builder e.g. `home/burley-yeomanry:git-3865c987/push`

**Note: these environment variables are case-sensitive**

### [deis/slugrunner](https://github.com/deis/slugrunner)

Slugrunner is configured and launched by the controller inside a Workflow cluster. If you are using slugrunner as a standalone component the following configuration is important:

- `SLUG_URL` - environment variable containing the path of the slug, relative to the builder storage location, e.g. `home/burley-yeomanry:git-3865c987/push/slug.tgz`

Slugrunner reads credential information from a `objectstorage-keyfile` secret in the current Kubernetes namespace.

### [deis/controller](https://github.com/deis/controller)

The controller is responsible for configuring the execution environment for buildpack-based applications. Controller copies `objectstorage-keyfile` into the application namespace so slugrunner can fetch the application slug.

The controller interacts through Kubernetes APIs and does not use any environment variables for object storage configuration.

### [deis/registry](https://github.com/deis/registry)

The registry looks for a `REGISTRY_STORAGE` environment variable which it then uses as a key to look up the object storage location and authentication information.

The registry reads credential information by reading `/var/run/secrets/deis/registry/creds/objectstorage-keyfile`.

This is the file location for the `objectstorage-keyfile` secret on the Pod filesystem.

### [deis/database](https://github.com/deis/postgres)

The database looks for a `DATABASE_STORAGE` environment variable, which it then uses as a key to look up the object storage location and authentication information

Minio (`DATABASE_STORAGE=minio`):

* `AWS_ACCESS_KEY_ID` via /var/run/secrets/deis/objectstore/creds/accesskey
* `AWS_SECRET_ACCESS_KEY` via /var/run/secrets/deis/objectstore/creds/secretkey
* `AWS_DEFAULT_REGION` is the Minio default of "us-east-1"
* `BUCKET_NAME` is the on-cluster default of "dbwal"

AWS (`DATABASE_STORAGE=s3`):

* `AWS_ACCESS_KEY_ID` via /var/run/secrets/deis/objectstore/creds/accesskey
* `AWS_SECRET_ACCESS_KEY` via /var/run/secrets/deis/objectstore/creds/secretkey
* `AWS_DEFAULT_REGION` via /var/run/secrets/deis/objectstore/creds/region
* `BUCKET_NAME` via /var/run/secrets/deis/objectstore/creds/database-bucket

GCS (`DATABASE_STORAGE=gcs`):

* `GS_APPLICATION_CREDS` via /var/run/secrets/deis/objectstore/creds/key.json
* `BUCKET_NAME` via /var/run/secrets/deis/objectstore/creds/database-bucket

Azure (`DATABASE_STORAGE=azure`):

* `WABS_ACCOUNT_NAME` via /var/run/secrets/deis/objectstore/creds/accountname
* `WABS_ACCESS_KEY` via /var/run/secrets/deis/objectstore/creds/accountkey
* `BUCKET_NAME` via /var/run/secrets/deis/objectstore/creds/database-container

[minio]: ../understanding-workflow/components.md#object-storage
[generate-params-toml]: https://github.com/deis/charts/blob/master/workflow-dev/tpl/generate_params.toml
