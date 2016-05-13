# Deploying an Application

An [Application][] is deployed to Deis using `git push` or the `deis` client.

## Supported Applications

Deis can deploy any application or service that can run inside a Docker container.  In order to be scaled horizontally, applications must follow the [Twelve-Factor App][] methodology and store any application state in external backing services.

For example, if your application persists state to the local filesystem -- common with content management systems like Wordpress and Drupal -- it cannot be scaled horizontally using `deis scale`.

Fortunately, most modern applications feature a stateless application tier that can scale horizontally inside Deis.


## Login to the Controller

!!! important
	if you haven't yet, now is a good time to [install the client][install client] and [register](../using-workflow/users-and-registration.md).

Before deploying an application, users must first authenticate against the Deis [Controller][]
using the URL supplied by their Deis administrator.

    $ deis login http://deis.example.com
    username: deis
    password:
    Logged in as deis

## Upload Your SSH Public Key

If you plan on using `git push` to deploy applications to Deis, you must provide your SSH public key.  Use the `deis keys:add` command to upload your default SSH public key, usually one of:

* ~/.ssh/id_rsa.pub
* ~/.ssh/id_dsa.pub

```
    $ deis keys:add
    Found the following SSH public keys:
    1) id_rsa.pub
    Which would you like to use with Deis? 1
    Uploading /Users/myuser/.ssh/id_rsa.pub to Deis... done
```

## Select a Build Process

Deis supports three different ways of building applications:

### Buildpacks

Heroku buildpacks are useful if you want to follow Heroku's best practices for building applications or if you are porting an application from Heroku.

Learn how to deploy applications [using Buildpacks](../applications/using-buildpacks.md).


### Dockerfiles

Dockerfiles are a powerful way to define a portable execution environment built on a base OS of your choosing.

Learn how to deploy applications [using Dockerfiles](../applications/using-dockerfiles.md).


### Docker Image

Deploying a Docker image onto Deis allows you to take a Docker image from either a public
or a private registry and copy it over bit-for-bit, ensuring that you are running the same
image in development or in your CI pipeline as you are in production.

Learn how to deploy applications [using Docker images](../applications/using-docker-images.md).

[install client]: ../using-workflow/cli.md#installation
[application]: ../reference-guide/terms.md#application
[controller]: ../understanding-workflow/components.md#controller
[Twelve-Factor App]: http://12factor.net/
