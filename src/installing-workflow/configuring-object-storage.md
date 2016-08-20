# Configuring Object Storage

A variety of Deis Workflow components rely on an object storage system to do their work including storing application slugs, Docker images and database logs.

Deis Workflow ships with [Minio][minio] by default, which provides in-cluster, ephemeral object storage. This means that _if the Minio server crashes, all data will be lost_. Therefore, **Minio should be used for development or testing only**.

## Configuring off-cluster Object Storage

Every component that relies on object storage uses two inputs for configuration:

1. Component-specific environment variables (e.g. `BUILDER_STORAGE` and `REGISTRY_STORAGE`)
2. Access credentials stored as a Kubernetes secret named `objectstorage-keyfile`

The helm classic chart for Deis Workflow can be easily configured to connect Workflow components to off-cluster object storage. Deis Workflow currently supports Google Compute Storage, Amazon S3, Azure Blob Storage and OpenStack Swift Storage.

### Step 1: Create storage buckets

Create storage buckets for each of the Workflow subsystems: `builder`, `registry`, and `database`.

Depending on your chosen object storage you may need to provide globally unique bucket names.

If you provide credentials with sufficient access to the underlying storage, Workflow components will create the buckets if they do not exist.

### Step 2: Generate storage credentials

If applicable, generate credentials that have create and write access to the storage buckets created in Step 1.

If you are using AWS S3 and your Kubernetes nodes are configured with appropriate IAM API keys via InstanceRoles, you do not need to create API credentials. Do, however, validate that the InstanceRole has appropriate permissions to the configured buckets!

### Step 3: Fetch Workflow charts

If you haven't already fetched the Helm Classic chart, do so with `helmc fetch deis/workflow-v2.4.1`

### Step 4: Configure Workflow charts

Operators should configure object storage by either populating a set of environment variables or editing the the Helm Classic parameters file before running `helmc generate`. Both options are documented below:

**Option 1:** Using environment variables

| Storage Type | Required Variables                                                                                                                                          | Notes                                                                                               |
| ---          | ---                                                                                                                                                         | ---                                                                                                 |
| s3           | `AWS_ACCESS_KEY`, `AWS_SECRET_KEY`, `AWS_REGISTRY_BUCKET`, `AWS_DATABASE_BUCKET`, `AWS_BUILDER_BUCKET`, `S3_REGION`                                         | To use [IAM credentials][aws-iam], it is not necessary to set `AWS_ACCESS_KEY` or `AWS_SECRET_KEY`. |
| gcs          | `GCS_KEY_JSON`, `GCS_REGISTRY_BUCKET`, `GCS_DATABASE_BUCKET`, `GCS_BUILDER_BUCKET`                                                                          |                                                                                                     |
| azure        | `AZURE_ACCOUNT_NAME`, `AZURE_ACCOUNT_KEY`, `AZURE_REGISTRY_CONTAINER`, `AZURE_DATABASE_CONTAINER`, `AZURE_BUILDER_CONTAINER`                                |                                                                                                     |
| swift        | `SWIFT_USERNAME`, `SWIFT_PASSWORD`, `SWIFT_AUTHURL`, `SWIFT_AUTHVERSION`, `SWIFT_REGISTRY_CONTAINER`, `SWIFT_DATABASE_CONTAINER`, `SWIFT_BUILDER_CONTAINER` | To specify tenant set `SWIFT_TENANT` if the auth version is 2 or later.                             |

!!! note
	These environment variables should be set **before** running `helmc generate` in Step 5.

**Option 2:** Using template file `tpl/generate_params.toml`

* Edit Helm Classic chart by running `helmc edit workflow-v2.4.1` and look for the template file `tpl/generate_params.toml`
* Update the `storage` parameter to reference the platform you are using, e.g. `s3`, `azure`, `gcs`, or `swift`
* Find the corresponding section for your storage type and provide appropriate values including region, bucket names, and access credentials.
* Save your changes to `tpl/generate_params.toml`.

!!! note
	You do not need to base64 encode any of these values as Helm Classic will handle encoding automatically.

### Step 5: Generate manifests

Generate the Workflow chart by running `helmc generate -x manifests workflow-v2.4.1`.

### Step 6: Verify credentials

Helm Classic stores the object storage configuration as a Kubernetes secret.

You may check the contents of the generated file named `deis-objectstorage-secret.yaml` in the `helmc` workspace directory:
```
$ cat $(helmc home)/workspace/charts/workflow-v2.4.1/manifests/deis-objectstorage-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: objectstorage-keyfile
...
data:
  accesskey: bm9wZSBub3BlCg==
  secretkey: c3VwZXIgbm9wZSBub3BlIG5vcGUgbm9wZSBub3BlCg==
  region: ZWFyZgo=
  registry-bucket: bXlmYW5jeS1yZWdpc3RyeS1idWNrZXQK
  database-bucket: bXlmYW5jeS1kYXRhYmFzZS1idWNrZXQK
  builder-bucket: bXlmYW5jeS1idWlsZGVyLWJ1c2tldAo=
```

You are now ready to `helmc install workflow-v2.4.1` using your desired object storage.

## Object Storage Configuration and Credentials

During the `helmc generate` step, Helm Classic creates a Kubernetes secret in the Deis namespace named `objectstorage-keyfile`. The exact structure of the file depends on storage backend specified in `tpl/generate_params.toml`.

```
# Set the storage backend
#
# Valid values are:
# - s3: Store persistent data in AWS S3 (configure in S3 section)
# - azure: Store persistent data in Azure's object storage
# - gcs: Store persistent data in Google Cloud Storage
# - minio: Store persistent data on in-cluster Minio server
# - swift: Store persistent data in OpenStack Swift object storage cluster
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

!!! note
	These environment variables are case-sensitive.

### [deis/slugrunner](https://github.com/deis/slugrunner)

Slugrunner is configured and launched by the controller inside a Workflow cluster. If you are using slugrunner as a standalone component the following configuration is important:

- `SLUG_URL` - environment variable containing the path of the slug, relative to the builder storage location, e.g. `home/burley-yeomanry:git-3865c987/push/slug.tgz`

Slugrunner reads credential information from a `objectstorage-keyfile` secret in the current Kubernetes namespace.

### [deis/dockerbuilder](https://github.com/deis/dockerbuilder)

Dockerbuilder is configured and launched by the builder component. Dockerbuilder reads credential information from the standard `objectstorage-keyfile` secret.

If you are using dockerbuilder as a standalone component the following configuration is important:

- `TAR_PATH` - The location of the application `.tar` archive, relative to the configured bucket for builder e.g. `home/burley-yeomanry:git-3865c987/tar`

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

Swift (`DATABASE_STORAGE=swift`):

* `SWIFT_USERNAME` via /var/run/secrets/deis/objectstore/creds/username
* `SWIFT_PASSWORD` via /var/run/secrets/deis/objectstore/creds/password
* `SWIFT_AUTHURL` via /var/run/secrets/deis/objectstore/creds/authurl
* `SWIFT_AUTHVERSION` via /var/run/secrets/deis/objectstore/creds/authversion
* `SWIFT_TENANT` via /var/run/secrets/deis/objectstore/creds/tenant
* `BUCKET_NAME` via /var/run/secrets/deis/objectstore/creds/database-container

[minio]: ../understanding-workflow/components.md#object-storage
[generate-params-toml]: https://github.com/deis/charts/blob/master/workflow-dev/tpl/generate_params.toml
[aws-iam]: http://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html
