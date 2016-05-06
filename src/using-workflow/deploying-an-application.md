# Deploying an Application

An [Application][] is deployed to Deis using `git push` or the `deis` client.


## Supported Applications

Deis can deploy any application or service that can run inside a Docker container.  In order to be scaled horizontally, applications must follow the [Twelve-Factor App][] methodology and store any application state in external backing services.

For example, if your application persists state to the local filesystem -- common with content management systems like Wordpress and Drupal -- it cannot be scaled horizontally using `deis scale`.

Fortunately, most modern applications feature a stateless application tier that can scale horizontally inside Deis.


## Login to the Controller

!!! important
	if you haven't yet, now is a good time to [install the client](installing-the-client.md) and [register](registering-a-user.md).

Before deploying an application, users must first authenticate against the Deis [Controller][]
using the URL supplied by their Deis administrator.

    $ deis login http://deis.example.com
    username: deis
    password:
    Logged in as deis


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

[application]: ../reference-guide/terms.md#application
[controller]: ../understanding-workflow/components.md#controller
[Twelve-Factor App]: http://12factor.net/
