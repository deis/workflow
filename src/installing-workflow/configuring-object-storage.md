# Configuring Object Storage

A variety of Deis Workflow components rely on an object storage system to do their work including storing application slugs, Docker images and database logs.

Deis Workflow ships with [Minio][minio] by default, which provides in-cluster, ephemeral object storage. This means that _if the Minio server crashes, all data will be lost_. Therefore, **Minio should be used for development or testing only**.

## Configuring off-cluster Object Storage

Every component that relies on object storage uses two inputs for configuration:

1. Component-specific environment variables (e.g. `BUILDER_STORAGE` and `REGISTRY_STORAGE`)
2. Access credentials stored as a Kubernetes secret named `objectstorage-keyfile`

The helm chart for Deis Workflow can be easily configured to connect Workflow components to off-cluster object storage. Deis Workflow currently supports Google Compute Storage, Amazon S3, [Azure Blob Storage][] and OpenStack Swift Storage.

### Step 1: Create storage buckets

Create storage buckets for each of the Workflow subsystems: `builder`, `registry`, and `database`.

Depending on your chosen object storage you may need to provide globally unique bucket names. If you are using S3, use hyphens instead of periods in the bucket names. Using periods in the bucket name will cause an [ssl certificate validation issue with S3](https://forums.aws.amazon.com/thread.jspa?threadID=105357).

If you provide credentials with sufficient access to the underlying storage, Workflow components will create the buckets if they do not exist.

### Step 2: Generate storage credentials

If applicable, generate credentials that have create and write access to the storage buckets created in Step 1.

If you are using AWS S3 and your Kubernetes nodes are configured with appropriate [IAM][aws-iam] API keys via InstanceRoles, you do not need to create API credentials. Do, however, validate that the InstanceRole has appropriate permissions to the configured buckets!

### Step 3: Add Deis Repo

If you haven't already added the Helm repo, do so with `helm repo add deis https://charts.deis.com/workflow`

### Step 4: Configure Workflow Chart

Operators should configure object storage by editing the Helm values file before running `helm install`. To do so:

* Fetch the Helm values by running `helm inspect values deis/workflow > values.yaml`
* Update the `global/storage` parameter to reference the platform you are using, e.g. `s3`, `azure`, `gcs`, or `swift`
* Find the corresponding section for your storage type and provide appropriate values including region, bucket names, and access credentials.
* Save your changes.

!!! note
	All values will be automatically (base64) encoded _except_ the `key_json` values under `gcs`/`gcr`.  These must be base64-encoded.  This is to support cleanly passing said encoded text via `helm --set` cli functionality rather than attempting to pass the raw JSON data.  For example:

		$ helm install workflow --namespace deis \
			--set global.storage=gcs,gcs.key_json="$(cat /path/to/gcs_creds.json | base64 -w 0)"

You are now ready to run `helm install deis/workflow --namespace deis -f values.yaml` using your desired object storage.


[minio]: ../understanding-workflow/components.md#object-storage
[aws-iam]: http://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html
[Azure Blob Storage]: https://azure.microsoft.com/en-us/services/storage/blobs/
