# Configuring Registry

Deis Workflow's builder component relies on a registry for storing application docker images.

Deis Workflow ships with a [registry][registry] component by default, which provides an in-cluster Docker registry backed by the platform-configured [object storage][storage]. Operators might want to use an off-cluster registry for performance or security reasons.

## Configuring Off-Cluster Private Registry

Every component that relies on a registry uses two inputs for configuration:

1. Registry Location environment variable named `DEIS_REGISTRY_LOCATION`
2. Access credentials stored as a Kubernetes secret named `registry-secret`

The Helm chart for Deis Workflow can be easily configured to connect Workflow components to off-cluster registry. Deis Workflow supports external registries which provide either short-lived tokens that are valid only for a specified amount of time or long-lived tokens (basic username/password) which are valid forever for authenticating to them. For those registries which provide short lived tokens for authentication, Deis Workflow will generate and refresh them such that the deployed apps will only have access to the short-lived tokens and not to the actual credentials for the registries.

When using a private registry the docker images are no longer pulled by Deis Workflow Controller but rather are managed by [Kubernetes][]. This will increase security and overall speed, however the `port` information can no longer be discovered. Instead the `port` information can be set via `deis config:set PORT=<port>` prior to deploying the application.

Deis Workflow currently supports:

  1. Google Container Registry([gcr][gcr]).
  1. EC2 Container Registry([ecr][ecr]).
  1. off-cluster: Any provider which supports long-lived username/password authentication, such as [Azure Container Registry][acr], [Docker Hub][dockerhub], [quay.io][quay], or a self-hosted Docker registry.

## Configuration

  1. If you haven't already fetched the values file, do so with `helm inspect values deis/workflow > values.yaml`
  1. Update registry location details by modifying the values file:
    * Update the `registry_location` parameter to reference the registry location you are using: `off-cluster`, `ecr`, `gcr`
    * Update the values in the section which corresponds to your registry location type.

You are now ready to `helm install deis/workflow --namespace deis -f values.yaml` using your desired registry.

## Examples
Here we show how the relevant parts of the fetched `values.yaml` file might look like after configuring for a particular off-cluster registry:

### ECR

```
global:
...
  registry_location: "ecr"
...
registry-token-refresher:
  # Time in minutes after which the token should be refreshed.
  # Leave it empty to use the default provider time.
  token_refresh_time: ""
...
  ecr:
    # Your AWS access key. Leave it empty if you want to use IAM credentials.
    accesskey: "ACCESS_KEY"
    # Your AWS secret key. Leave it empty if you want to use IAM credentials.
    secretkey: "SECRET_KEY"
    # Any S3 region
    region: "us-west-2"
    registryid: ""
    hostname: ""
...
```
**Note:** `registryid` and `hostname` should _not_ be set.  See [this issue](https://github.com/deis/registry-token-refresher/issues/11) for more info.

### GCR

```
global:
...
  registry_location: "gcr"
...
registry-token-refresher:
  # Time in minutes after which the token should be refreshed.
  # Leave it empty to use the default provider time.
  token_refresh_time: ""
...
  gcr:
    key_json: <base64-encoded JSON data>
    hostname: ""
```

**Note:** `hostname` should be left empty.

### [Azure Container Registry](https://azure.microsoft.com/en-us/services/container-registry/) (ACR)

After following the [docs](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-azure-cli) and creating a registry, e.g. `myregistry`, with its corresponding login server of `myregistry.azurecr.io`, the following values should be supplied:

```
global:
...
  registry_location: "off-cluster"
...
registry-token-refresher:
...
  off_cluster_registry:
    hostname: "myregistry.azurecr.io"
    organization: "myorg"
    username: "myusername"
    password: "mypassword"
...
```

**Note:** The mandatory organization field (here `myorg`) will be created as an ACR repository if it does not already exist.

### Quay.io

```
global:
...
  registry_location: "off-cluster"
...
registry-token-refresher:
...
  off_cluster_registry:
    hostname: "quay.io"
    organization: "myorg"
    username: "myusername"
    password: "mypassword"
...
```

[registry]: ../understanding-workflow/components.md#registry
[storage]: configuring-object-storage
[ecr]: http://docs.aws.amazon.com/AmazonECR/latest/userguide/ECR_GetStarted.html
[gcr]: https://cloud.google.com/container-registry/
[acr]: https://docs.microsoft.com/en-us/azure/container-registry/
[dockerhub]: https://hub.docker.com/
[quay]: https://quay.io/
[srvAccount]: https://support.google.com/cloud/answer/6158849#serviceaccounts
[aws-iam]: https://aws.amazon.com/iam/
[namespace]: https://docs.docker.com/registry/spec/api/#/overview
[Kubernetes]: https://kubernetes.io
