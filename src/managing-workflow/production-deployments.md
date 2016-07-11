# Production Deployments

When readying a Workflow deployment for production workloads, there are some additional
recommendations.


## Running Workflow without Minio

Workflow makes use of [Minio][] to provide storage for the [Registry][], [Database][], and
[Logger][] components. Minio is provided out of the box as a central storage compartment, but it is
not resilient to cluster outages. If Minio is shut down, all data is lost.

In production, persistent storage can be achieved by running an external object store.
For users on AWS, GCE/GKE or Azure, the convenience of Amazon S3, Google GCS or Microsoft Azure Storage
makes the prospect of running a Minio-less Workflow cluster quite reasonable. For users who have restriction
on using external object storage using swift object storage can be an option.

Running a Workflow cluster without Minio provides several advantages:

 - Removal of state from the worker nodes
 - Reduced resource usage
 - Reduced complexity and operational burden of managing Workflow

See [Configuring Object Storage][] for details on removing this operational complexity.


## Review Security Considerations

There are some additional security-related considerations when running Workflow in production, and
users can consider enabling a firewall on the CoreOS hosts as well as the router component.

See [Security Considerations][] for details.


## Change Registration Mode

Changing the registration process is highly recommended in production. By default, registrations
for a new cluster are open to anyone with the proper URL. Once the admin user has registered with a
new cluster, it is recommended to either turn off registrations or enable the admin-only
registration feature.

Please see the following documentation: [Customizing Controller][]


## Enable TLS

Using TLS to encrypt traffic (including Workflow client traffic, such as login credentials) is
crucial. See [Platform SSL][] for the platform.


[configuring object storage]: ../installing-workflow/configuring-object-storage.md
[customizing controller]: tuning-component-settings.md#customizing-the-controller
[database]: ../understanding-workflow/components.md#database
[logger]: ../understanding-workflow/components.md#logger
[minio]: ../understanding-workflow/components.md#minio
[platform ssl]: platform-ssl.md
[registry]: ../understanding-workflow/components.md#registry
[security considerations]: security-considerations.md
