# Configure Object Storage

A variety of Deis components rely on an object storage system to do their work. These components are:

- [workflow](https://github.com/deis/workflow)
- [builder](https://github.com/deis/builder)
- [slugbuilder](https://github.com/deis/slugbuilder)
- [slugrunner](https://github.com/deis/slugrunner)
- [registry](https://github.com/deis/registry)

These components are built flexibly, so they can work out of the box with almost any system that is compatible with the [S3 API](http://docs.aws.amazon.com/AmazonS3/latest/API/APIRest.html).

# Minio

Additionally, Deis ships with a [Minio](http://minio.io) [component](https://github.com/deis/minio). This component runs as a Kubernetes service, and the components listed above are configured to automatically look for that service and use it as object storage if it's available.

# Telling Deis What to Use

The Deis components determine what object storage system to use via environment variables that you set up:

- `DEIS_MINIO_SERVICE_HOST` and `DEIS_MINIO_SERVICE_PORT` - The in-cluster Minio service
- `DEIS_OUTSIDE_STORAGE_HOST` and `DEIS_OUTSIDE_STORAGE_PORT` - The external S3-compatible object storage system

# Limitations

- In some cases, the minio service must be started up before other components, so that they see the Minio service's environment variables. If you use [helm](https://github.com/helm/helm) to install deis, this ordering won't be ensured. (builder, slugbuilder and slugrunner are fine)
- Registry doesn't currently automatically look up the minio service, nor will it look for other storage env vars.
