# Configure Object Storage

A variety of Deis components rely on an object storage system to do their work. These components are:

- [builder](https://github.com/deis/builder)
- [slugbuilder](https://github.com/deis/slugbuilder)
- [slugrunner](https://github.com/deis/slugrunner)
- [controller](https://github.com/deis/controller)
- [registry](https://github.com/deis/registry)
- [database](https://github.com/deis/postgres)

These components are flexible and can work out of the box with almost any system that is compatible with the [S3 API](http://docs.aws.amazon.com/AmazonS3/latest/API/APIRest.html).

## Minio

Additionally, Deis ships with a [Minio](http://minio.io) [component](https://github.com/deis/minio) by default, which provides in-cluster, ephemeral object storage. This means that _if the Minio server crashes, all data will be lost_. Therefore, **Minio should be used for development or testing only**.

In our beta release, the components listed above are configured by default to automatically use the Minio [service][k8s-service] for object storage.

# Configuring the Deis Components

Every Deis component that relies on object storage relies on the following two inputs for configuration:

- An environment variable that describe what object storage system to use.
- A configuration file ([objectstorage.toml][objectstorage-toml]) to provide access credentials for the object storage system.
	- We suggest storing the contents of these files in [Kubernetes secrets][k8s-secret] and mounting them as volumes to each pod.
	- See [the workflow-dev chart](https://github.com/deis/charts/tree/master/workflow-dev) for examples of using and mounting secrets.

The subsections herein explain how to configure these two inputs for each applicable component.

## [deis/builder](https://github.com/deis/builder)

### Environment Variables

The builder looks for a `BUILDER_STORAGE` environment variable, which it then uses as a key to look up the object storage location and authentication information in a configuration file. See below for details on that file.

### Credentials

The builder reads the credential information from a `objectstorage-keyfile` secret. This is generated automatically (as part of the `helm generate` command) based on the configuration options given in the [objectstorage.toml file][objectstorage-toml] file.

### Helm Chart

If you are using the [Helm Chart for Workflow][helm-chart], put your credentials in the [objectstorage.toml][objectstorage-toml] file before you run `helm generate`. Note that you don't need to base64-encode the credentials, as Helm will do that for you. For more information, see the [installation instructions][helm-install] for more details on using Helm.

## [deis/slugbuilder](https://github.com/deis/slugbuilder)

The slugbuilder is configured and launched by the builder inside a Deis cluster, so this section only applies if you intend to run it as a standalone component.

### Environment Variables

The slugbuilder looks for the below environment variables to determine where to download code from and upload slugs to.

- `TAR_PATH` - The location of the `.tar` archive (which it will build)
- `PUT_PATH` - The location this component will upload the finished slug to

Note that these environment variables are case-sensitive.

### Credentials

The slugbuilder reads the credential information from a `objectstorage-keyfile` secret. This is generated automatically (as part of the `helm generate` command) based on the configuration options given in the [objectstorage.toml file][objectstorage-toml] file.

### Helm Chart

The [Helm Chart for Workflow][helm-chart] contains no manifest for the slugbuilder. As noted above, the builder handles all configuration and lifecycle management for you.

If, however, you wish to run the slugbuilder as a standalone component, you can use the `objectstorage-keyfile` secret to easily provide your pods with the credentials information they need. This is generated automatically (as part of the `helm generate` command) based on the configuration options given in the [objectstorage.toml file][objectstorage-toml] file.

## [deis/slugrunner](https://github.com/deis/slugrunner)

The slugrunner is configured and launched by the controller inside a Deis cluster, so this section only applies if you intend to run it as a standalone component.

### Environment Variables

The slugrunner uses the `SLUG_URL` environment variable to determine where to download the slug (that it will run) from.

### Credentials

The slugrunner reads the credential information from a `objectstorage-keyfile` secret. This is generated automatically (as part of the `helm generate` command) based on the configuration options given in the [objectstorage.toml file][objectstorage-toml] file.

### Helm Chart

The [Helm Chart for Workflow][helm-chart] contains no manifest for the slugrunner. As noted above, the controller handles all configuration and lifecycle management for you.

If, however, you wish to run the slugrunner as a standalone component, you can use the `objectstorage-keyfile` secret to easily provide your pods with the credentials information they need. This is generated automatically (as part of the `helm generate` command) based on the configuration options given in the [objectstorage.toml file][objectstorage-toml] file.

## [deis/controller](https://github.com/deis/controller)

When the controller needs to launch or scale a new buildpack application, it uses a [replication controller](http://kubernetes.io/docs/user-guide/replication-controller/). Since the slugrunner needs to download the slug to run, it needs the object storage location of the slug and the object storage credentials.

### Environment Variables

The controller needs no environment variables for object storage configuration.

### Credentials

Since the object storage location information comes from the builder, the controller only needs access to the credentials information. The controller gets this information by accessing the `minio-user` secret (even if it's not using Minio as the object storage system) directly from the Kubernetes API.

No paths need to be mounted into the pod. Simply ensure that the secret exists in your Kubernetes cluster with the correct credentials.

### Helm Chart

If you are using the [Helm Chart for Workflow][helm-chart], put your credentials in the [objectstorage.toml][objectstorage-toml] file before you run `helm generate`. Note that you don't need to base64-encode the credentials, as Helm will do that for you. For more information, see the [installation instructions][helm-install] for more details on using Helm.

## [deis/registry](https://github.com/deis/registry)

The registry is configured slightly differently from most of the other components. Read on for details.

### Environment Variables

The registry looks for a `REGISTRY_STORAGE` environment variable, which it then uses as a key to look up the object storage location and authentication information in a configuration file. See below for details on that file.

### Credentials

The registry reads the credential information from a `/var/run/secrets/deis/registry/creds/objectstorage-keyfile` file. This is generated automatically (as part of the `helm generate` command) based on the configuration options given in the [objectstorage.toml file][objectstorage-toml] file.

### Helm Chart

If you are using the [Helm Chart for Workflow][helm-chart], put your credentials in the [objectstorage.toml][objectstorage-toml] file before you run `helm generate`. Note that you don't need to base64-encode the credentials, as Helm will do that for you. For more information, see the [installation instructions][helm-install] for more details on using Helm.

## [deis/database](https://github.com/deis/postgres)

### Environment Variables

The database looks for a `DATABASE_STORAGE` environment variable, which it then uses as a key to look up the object storage location and authentication information in a configuration file. See below for details on that file.

### Credentials

The database reads the credential information from a `objectstorage-keyfile` secret. This is generated automatically (as part of the `helm generate` command) based on the configuration options given in the [objectstorage.toml file][objectstorage-toml] file.

### Helm Chart

If you are using the [Helm Chart for Workflow][helm-chart], put your credentials in the [objectstorage.toml][objectstorage-toml] file before you run `helm generate`. Note that you don't need to base64-encode the credentials, as Helm will do that for you. For more information, see the [installation instructions][helm-install] for more details on using Helm.


[helm-chart]: https://github.com/deis/charts/tree/master/workflow-dev
[minio-user-secret]: https://github.com/deis/charts/blob/master/workflow-dev/manifests/deis-minio-secret-user.yaml
[helm-install]: https://github.com/deis/workflow/blob/master/src/installing-workflow/installing-deis-workflow.md
[objectstorage-toml]: https://github.com/deis/charts/blob/master/workflow-dev/tpl/objectstorage.toml
[k8s-service]: http://kubernetes.io/docs/user-guide/services/
[k8s-secret]: http://kubernetes.io/docs/user-guide/secrets/
