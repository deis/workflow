# Using Buildpacks

Deis supports deploying applications via [Heroku Buildpacks][]. Buildpacks are useful if you're interested in following Heroku's best practices for building applications or if you are deploying an application that already runs on Heroku.

## Add SSH Key
 
For **Buildpack** based application deploys via `git push`, Deis Workflow identifies users via SSH keys. SSH keys are pushed to the platform and must be unique to each user.

- See [this document](../users/ssh-keys.md/#generate-an-ssh-key) for instructions on how to generate an SSH key.

- Run `deis keys:add` to upload your SSH key to Deis Workflow.

```
$ deis keys:add ~/.ssh/id_deis.pub
Uploading id_deis.pub to deis... done
```

Read more about adding/removing SSH Keys [here](../users/ssh-keys.md/#adding-and-removing-ssh-keys).

## Prepare an Application

If you do not have an existing application, you can clone an example application that demonstrates the Heroku Buildpack workflow.

    $ git clone https://github.com/deis/example-go.git
    $ cd example-go


## Create an Application

Use `deis create` to create an application on the [Controller][].

    $ deis create
    Creating application... done, created skiing-keypunch
    Git remote deis added


## Push to Deploy

Use `git push deis master` to deploy your application.

    $ git push deis master
    Counting objects: 75, done.
    Delta compression using up to 8 threads.
    Compressing objects: 100% (48/48), done.
    Writing objects: 100% (75/75), 18.28 KiB | 0 bytes/s, done.
    Total 75 (delta 30), reused 58 (delta 22)
    Starting build... but first, coffee!
    -----> Go app detected
    -----> Checking Godeps/Godeps.json file.
    -----> Installing go1.4.2... done
    -----> Running: godep go install -tags heroku ./...
    -----> Discovering process types
           Procfile declares types -> web
    -----> Compiled slug size is 1.7M
    Build complete.
    Launching app.
    Launching...
    Done, skiing-keypunch:v2 deployed to Deis

    Use 'deis open' to view this application in your browser

    To learn more, use 'deis help' or visit http://deis.io

    To ssh://git@deis.staging-2.deis.com:2222/skiing-keypunch.git
     * [new branch]      master -> master

    $ curl -s http://skiing-keypunch.example.com
    Powered by Deis
    Release v2 on skiing-keypunch-v2-web-02zb9

Because a Heroku-style application is detected, the `web` process type is automatically scaled to 1 on first deploy.

Use `deis scale web=3` to increase `web` processes to 3, for example. Scaling a
process type directly changes the number of [pods] running that process.


## Included Buildpacks

For convenience, a number of buildpacks come bundled with Deis:

 * [Ruby Buildpack][]
 * [Nodejs Buildpack][]
 * [Java Buildpack][]
 * [Gradle Buildpack][]
 * [Grails Buildpack][]
 * [Play Buildpack][]
 * [Python Buildpack][]
 * [PHP Buildpack][]
 * [Clojure Buildpack][]
 * [Scala Buildpack][]
 * [Go Buildpack][]
 * [Multi Buildpack][]

Deis will cycle through the `bin/detect` script of each buildpack to match the code you
are pushing.

!!! note
    If you're testing against the [Scala Buildpack][], the [Builder][] requires at least
    512MB of free memory to execute the Scala Build Tool.


## Using a Custom Buildpack

To use a custom buildpack, set the `BUILDPACK_URL` environment variable.

    $ deis config:set BUILDPACK_URL=https://github.com/dpiddy/heroku-buildpack-ruby-minimal
    Creating config... done, v2

    === humble-autoharp
    BUILDPACK_URL: https://github.com/dpiddy/heroku-buildpack-ruby-minimal

!!! note
    If, however, you're unable to deploy using the latest version of the buildpack, You can set an exact version of a buildpack by using a git revision in your `BUILDPACK_URL`. For example: `BUILDPACK_URL=https://github.com/dpiddy/heroku-buildpack-ruby-minimal#v13`

On your next `git push`, the custom buildpack will be used.


## Compile Hooks

Sometimes, an application needs a way to stop or check if a service is running before building an
app, which may require notifying a service that the [Builder][] has finished compiling the app. In
order to do this, an app can provide two files in their `bin/` directory:

```
bin/pre-compile
bin/post-compile
```

The builder will run these commands before and after the build process, respectively.


## Using Private Repositories

To pull code from private repositories, set the `SSH_KEY` environment variable to a private key
which has access. Use either the path of a private key file or the raw key material:

    $ deis config:set SSH_KEY=/home/user/.ssh/id_rsa
    $ deis config:set SSH_KEY="""-----BEGIN RSA PRIVATE KEY-----
    (...)
    -----END RSA PRIVATE KEY-----"""

For example, to use a custom buildpack hosted at a private GitHub URL, ensure that an SSH public
key exists in your [GitHub settings][]. Then set `SSH_KEY` to the corresponding SSH private key
and set `BUILDPACK_URL` to the URL:

    $ deis config:set SSH_KEY=/home/user/.ssh/github_id_rsa
    $ deis config:set BUILDPACK_URL=git@github.com:user/private_buildpack.git
    $ git push deis master


[pods]: http://kubernetes.io/v1.1/docs/user-guide/pods.html
[controller]: ../understanding-workflow/components.md#controller
[builder]: ../understanding-workflow/components.md#builder
[Ruby Buildpack]: https://github.com/heroku/heroku-buildpack-ruby
[Nodejs Buildpack]: https://github.com/heroku/heroku-buildpack-nodejs
[Java Buildpack]: https://github.com/heroku/heroku-buildpack-java
[Gradle Buildpack]: https://github.com/heroku/heroku-buildpack-gradle
[Grails Buildpack]: https://github.com/heroku/heroku-buildpack-grails
[Play Buildpack]: https://github.com/heroku/heroku-buildpack-play
[Python Buildpack]: https://github.com/heroku/heroku-buildpack-python
[PHP Buildpack]: https://github.com/heroku/heroku-buildpack-php
[Clojure Buildpack]: https://github.com/heroku/heroku-buildpack-clojure
[Scala Buildpack]: https://github.com/heroku/heroku-buildpack-scala
[Go Buildpack]: https://github.com/kr/heroku-buildpack-go
[Multi Buildpack]: https://github.com/heroku/heroku-buildpack-multi
[Heroku Buildpacks]: https://devcenter.heroku.com/articles/buildpacks
[GitHub settings]: https://github.com/settings/ssh
