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

There are some additional security-related considerations when running Workflow in production.
See [Security Considerations][] for details.


## Registration is Admin-Only

By default, registration with the Workflow controller is in "admin_only" mode. The first user
to run a `deis register` command becomes the initial "admin" user, and registrations after that
are disallowed unless requested by an admin.

Please see the following documentation to learn about changing registration mode:

 - [Customizing Controller][]

## Disable Grafana Signups

It is also recommended to disable signups for the Grafana dashboards.

Please see the following documentation to learn about disabling Grafana signups:

 - [Customizing Monitor][]


## Enable TLS

Using TLS to encrypt traffic (including Workflow client traffic, such as login credentials) is
crucial. See [Platform SSL][] for the platform.

## Scale Routers

If all router pods in your cluster become unavailable then you will be unable to access the workflow API or
any deployed applications. To reduce the potential of this happening it is recommended that you scale the
deis-router Deployment to run more than one router pod. This can be accomplished by running
`kubectl --namespace=deis scale --replicas=2 deployment/deis-router`

[configuring object storage]: ../installing-workflow/configuring-object-storage.md
[customizing controller]: tuning-component-settings.md#customizing-the-controller
[customizing monitor]: tuning-component-settings.md#customizing-the-monitor
[database]: ../understanding-workflow/components.md#database
[logger]: ../understanding-workflow/components.md#logger
[minio]: ../understanding-workflow/components.md#minio
[platform ssl]: platform-ssl.md
[registry]: ../understanding-workflow/components.md#registry
[security considerations]: security-considerations.md
