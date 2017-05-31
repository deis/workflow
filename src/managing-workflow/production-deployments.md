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

## Using on-cluster registry with CNI

If you are using [CNI](https://github.com/containernetworking/cni) for managing container network, you cannot use `hostPort` notation due to [this issue](https://github.com/kubernetes/kubernetes/issues/23920).
In this case you could enable CNI for `deis-registry-proxy` by setting `use_cni` variable to `true` inside `values.yaml` or by adding `--set global.use_cni=true` to `helm`'s args.

## Running Workflow with RBAC

If your cluster has [RBAC](https://kubernetes.io/docs/admin/authorization/rbac/) amongst your [authorization](https://kubernetes.io/docs/admin/authorization/) modes (`$ kubectl api-versions` should contains `rbac.authorization.k8s.io`) it may be necessary to enable RBAC in Workflow.
This can be achieved by setting `use_rbac` in the `global` section of `values.yaml` to `true`, or by adding `--set=global.use_rbac=true` to the `$ helm install/upgrade` command.
RBAC support was announced in Kubernetes-1.5 and is enabled by default if:
- your Kubernetes cluster is in GKE
- your Kubernetes cluster built with [kubeadm](https://kubernetes.io/docs/getting-started-guides/kubeadm/)

**Note**: helm may need to be given [specific permissions][helm specific permissions] under RBAC if not already done.

**Attention**: Azure ACS Kubernetes clusters are not RBAC-enabled for today due to lack in authentication strategy. Feel free to watch this [PR](https://github.com/kubernetes/kubernetes/pull/43987) for more details.

[configuring object storage]: ../installing-workflow/configuring-object-storage.md
[customizing controller]: tuning-component-settings.md#customizing-the-controller
[customizing monitor]: tuning-component-settings.md#customizing-the-monitor
[database]: ../understanding-workflow/components.md#database
[logger]: ../understanding-workflow/components.md#logger
[minio]: ../understanding-workflow/components.md#minio
[platform ssl]: platform-ssl.md
[registry]: ../understanding-workflow/components.md#registry
[security considerations]: security-considerations.md
[helm specific permissions]: ../installing-workflow/index.md#check-your-authorization
