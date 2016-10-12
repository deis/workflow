# Configuring Registry

Deis Workflow's builder component relies on registry for storing the application docker images.

Deis Workflow ships with a [registry][registry] component by default, which provides an in-cluster Docker registry backed by the platform-configured [object storage][storage]. Operators might want to use an off-cluster registry for performance or security reasons.

## Configuring Off-Cluster Private Registry

Every component that relies on registry uses two inputs for configuration:

1. Registry Location environment variable named `DEIS_REGISTRY_LOCATION`
2. Access credentials stored as a Kubernetes secret named `registry-secret`

The helm classic chart for Deis Workflow can be easily configured to connect Workflow components to off-cluster registry. Deis Workflow supports external registries which provide either short lived tokens which are valid only for a specified amount of time or long lived tokens(basic username/password) which are valid forever for authenticating to them. For those registries which provide short lived tokens for authentication Deis Workflow will generate and refresh them such that the deployed apps will only have access to the short lived tokens and not to the actual credentials for the registries.

When using a private registry the docker images are no longer pulled by Deis Workflow Controller but rather is managed by Kubernetes. This will increase security and overall speed, however the `port` information can no longer be discovered. Instead the `port` information can be set via `deis config:set PORT=<port>` prior to deploying the application.  
Deis Workflow currently supports
  1. Google Container Registry([gcr][gcr]).
  2. EC2 Container Registry([ecr][ecr]).
  3. off-cluster storage providers like dockerhub, quay.io, etc., or self hosted docker registry.

* **Step 1:** If you haven't already fetched the Helm Classic chart, do so with `helmc fetch deis/workflow-v2.7.0`
* **Step 2:** Update registry location details either by setting the appropriate environment variables _or_ by modifying the template file `tpl/generate_params.toml`. Note that environment variables take precedence over settings in `tpl/generate_params.toml`.
    * **1.** Using environment variables: Set `REGISTRY_LOCATION` to `off-cluster`, `ecr` or `gcr`, then set the following environment variables accordingly.
          * For `REGISTRY_LOCATION=gcr`:

            ```
            export GCR_KEY_JSON, GCR_HOSTNAME
            ```

            `GCR_KEY_JSON`: The contents of the [service account][srvAccount] JSON key file.  
            `GCR_HOSTNAME` can be empty and needs to be set if host name is different from "https://gcr.io".

          * For `REGISTRY_LOCATION=ecr`:

            ```
            export ECR_ACCESS_KEY, ECR_SECRET_KEY, ECR_REGION, ECR_REGISTRY_ID, ECR_HOSTNAME
            ```

              `ECR_ACCESS_KEY` and `ECR_SECRET_KEY` are an AWS access key ID and secret access key with permission to use the container registry. To use [IAM credentials][aws-iam], it is not necessary to set either value, in which case the credentials used to provision the cluster will be used.

              If `ECR_REGISTRY_ID` is empty, the default registry for the provisioning account will be used.

              `ECR_HOSTNAME` only needs to be set if the default hostname is an alias (CNAME) or if the cluster is behind a proxy.


          * For `REGISTRY_LOCATION=off-cluster`:

            ```
            export REGISTRY_USERNAME, REGISTRY_PASSWORD, REGISTRY_HOSTNAME, REGISTRY_ORGANIZATION
            ```

            If `REGISTRY_HOSTNAME` is not set then Workflow assumes it to be Dockerhub.  
            `REGISTRY_ORGANIZATION` can be left empty if there is no namespacing in the registry. A [namespace][namespace] is a collection of repositories with a common name prefix.

    * **2.** Using template file `tpl/generate_params.toml`:
          * Open the helm classic chart with `helmc edit workflow-v2.7.0` and look for the template file `tpl/generate_params.toml`
          * Update the `registry_location` parameter to reference the registry location you are using: `off-cluster`, `ecr`, `gcr`
          * Update the values in the section which corresponds to your registry location type.
      * Note: you do not need to base64 encode any of these values as Helm Classic will handle encoding automatically
* **Step 3:** Save your changes and re-generate the helm classic chart by running `helmc generate -x manifests workflow-v2.7.0`
* **Step 4:** Check the generated file in your manifests directory, you should see `deis-registry-secret.yaml`

        You are now ready to `helmc install workflow-v2.7.0` using your desired registry.

[registry]: ../understanding-workflow/components.md#registry
[storage]: configuring-object-storage
[ecr]: http://docs.aws.amazon.com/AmazonECR/latest/userguide/ECR_GetStarted.html
[gcr]: https://cloud.google.com/container-registry/
[srvAccount]: https://support.google.com/cloud/answer/6158849#serviceaccounts
[aws-iam]: https://aws.amazon.com/iam/
[namespace]: https://docs.docker.com/registry/spec/api/#/overview
