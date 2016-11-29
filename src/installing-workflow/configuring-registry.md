# Configuring Registry

Deis Workflow's builder component relies on registry for storing the application docker images.

Deis Workflow ships with a [registry][registry] component by default, which provides an in-cluster Docker registry backed by the platform-configured [object storage][storage]. Operators might want to use an off-cluster registry for performance or security reasons.

## Configuring Off-Cluster Private Registry

Every component that relies on registry uses two inputs for configuration:

1. Registry Location environment variable named `DEIS_REGISTRY_LOCATION`
2. Access credentials stored as a Kubernetes secret named `registry-secret`

The Helm chart for Deis Workflow can be easily configured to connect Workflow components to off-cluster registry. Deis Workflow supports external registries which provide either short-lived tokens which are valid only for a specified amount of time or long-lived tokens (basic username/password) which are valid forever for authenticating to them. For those registries which provide short lived tokens for authentication, Deis Workflow will generate and refresh them such that the deployed apps will only have access to the short-lived tokens and not to the actual credentials for the registries.

When using a private registry the docker images are no longer pulled by Deis Workflow Controller but rather is managed by Kubernetes. This will increase security and overall speed, however the `port` information can no longer be discovered. Instead the `port` information can be set via `deis config:set PORT=<port>` prior to deploying the application.
Deis Workflow currently supports
  1. Google Container Registry([gcr][gcr]).
  2. EC2 Container Registry([ecr][ecr]).
  3. off-cluster storage providers like dockerhub, quay.io, etc., or self hosted docker registry.

* **Step 1:** If you haven't already fetched the values file, do so with `helm inspect values deis/workflow | sed -n '1!p' > values.yaml`
* **Step 2:** Update registry location details by modifying the values file.
    * Update the `registry_location` parameter to reference the registry location you are using: `off-cluster`, `ecr`, `gcr`
    * Update the values in the section which corresponds to your registry location type.
    * Note: you do not need to base64 encode any of these values as Helm will handle encoding automatically

You are now ready to `helm install deis/workflow --namespace deis -f values.yaml` using your desired registry.

[registry]: ../understanding-workflow/components.md#registry
[storage]: configuring-object-storage
[ecr]: http://docs.aws.amazon.com/AmazonECR/latest/userguide/ECR_GetStarted.html
[gcr]: https://cloud.google.com/container-registry/
[srvAccount]: https://support.google.com/cloud/answer/6158849#serviceaccounts
[aws-iam]: https://aws.amazon.com/iam/
[namespace]: https://docs.docker.com/registry/spec/api/#/overview
