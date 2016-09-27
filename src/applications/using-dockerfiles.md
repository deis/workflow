# Using Dockerfiles

Deis supports deploying applications via Dockerfiles.  A [Dockerfile][] automates the steps for crafting a [Docker Image][].
Dockerfiles are incredibly powerful but require some extra work to define your exact application runtime environment.

## Add SSH Key

For **Dockerfile** based application deploys via `git push`, Deis Workflow identifies users via SSH keys. SSH keys are pushed to the platform and must be unique to each user.

- See [this document](../users/ssh-keys.md/#generate-an-ssh-key) for instructions on how to generate an SSH key.

- Run `deis keys:add` to upload your SSH key to Deis Workflow.

```
$ deis keys:add ~/.ssh/id_deis.pub
Uploading id_deis.pub to deis... done
```

Read more about adding/removing SSH Keys [here](../users/ssh-keys.md/#adding-and-removing-ssh-keys).


## Prepare an Application

If you do not have an existing application, you can clone an example application that demonstrates the Dockerfile workflow.

    $ git clone https://github.com/deis/helloworld.git
    $ cd helloworld


### Dockerfile Requirements

In order to deploy Dockerfile applications, they must conform to the following requirements:

* The Dockerfile must use the `EXPOSE` directive to expose exactly one port.
* That port must be listening for an HTTP connection.
* The Dockerfile must use the `CMD` directive to define the default process that will run within the container.
* The Docker image must contain [bash](https://www.gnu.org/software/bash/) to run processes.

!!! note
    Note that if you are using a private registry of any kind (`gcr` or other) the application environment must include a `$PORT` config variable that matches the `EXPOSE`'d port, example: `deis config:set PORT=5000`. See [Configuring Registry](../installing-workflow/configuring-registry/#configuring-off-cluster-private-registry) for more info.


## Create an Application

Use `deis create` to create an application on the [Controller][].

    $ deis create
    Creating application... done, created folksy-offshoot
    Git remote deis added


## Push to Deploy

Use `git push deis master` to deploy your application.

    $ git push deis master
    Counting objects: 13, done.
    Delta compression using up to 8 threads.
    Compressing objects: 100% (13/13), done.
    Writing objects: 100% (13/13), 1.99 KiB | 0 bytes/s, done.
    Total 13 (delta 2), reused 0 (delta 0)
    -----> Building Docker image
    Uploading context 4.096 kB
    Uploading context
    Step 0 : FROM deis/base:latest
     ---> 60024338bc63
    Step 1 : RUN wget -O /tmp/go1.2.1.linux-amd64.tar.gz -q https://go.googlecode.com/files/go1.2.1.linux-amd64.tar.gz
     ---> Using cache
     ---> cf9ef8c5caa7
    Step 2 : RUN tar -C /usr/local -xzf /tmp/go1.2.1.linux-amd64.tar.gz
     ---> Using cache
     ---> 515b1faf3bd8
    Step 3 : RUN mkdir -p /go
     ---> Using cache
     ---> ebf4927a00e9
    Step 4 : ENV GOPATH /go
     ---> Using cache
     ---> c6a276eded37
    Step 5 : ENV PATH /usr/local/go/bin:/go/bin:$PATH
     ---> Using cache
     ---> 2ba6f6c9f108
    Step 6 : ADD . /go/src/github.com/deis/helloworld
     ---> 94ab7f4b977b
    Removing intermediate container 171b7d9fdb34
    Step 7 : RUN cd /go/src/github.com/deis/helloworld && go install -v .
     ---> Running in 0c8fbb2d2812
    github.com/deis/helloworld
     ---> 13b5af931393
    Removing intermediate container 0c8fbb2d2812
    Step 8 : ENV PORT 80
     ---> Running in 9b07da36a272
     ---> 2dce83167874
    Removing intermediate container 9b07da36a272
    Step 9 : CMD ["/go/bin/helloworld"]
     ---> Running in f7b215199940
     ---> b1e55ce5195a
    Removing intermediate container f7b215199940
    Step 10 : EXPOSE 80
     ---> Running in 7eb8ec45dcb0
     ---> ea1a8cc93ca3
    Removing intermediate container 7eb8ec45dcb0
    Successfully built ea1a8cc93ca3
    -----> Pushing image to private registry

           Launching... done, v2

    -----> folksy-offshoot deployed to Deis
           http://folksy-offshoot.local3.deisapp.com

           To learn more, use `deis help` or visit http://deis.io

    To ssh://git@local3.deisapp.com:2222/folksy-offshoot.git
     * [new branch]      master -> master

    $ curl -s http://folksy-offshoot.local3.deisapp.com
    Welcome to Deis!
    See the documentation at http://docs.deis.io/ for more information.

Because a Dockerfile application is detected, the `cmd` process type is automatically scaled to 1 on first deploy.

Use `deis scale cmd=3` to increase `cmd` processes to 3, for example. Scaling a
process type directly changes the number of [containers][container]
running that process.

[container]: ../reference-guide/terms.md#container
[controller]: ../understanding-workflow/components.md#controller
[Dockerfile]: https://docs.docker.com/reference/builder/
[Docker Image]: https://docs.docker.com/introduction/understanding-docker/
[CMD instruction]:  https://docs.docker.com/reference/builder/#cmd
[Procfile]: https://devcenter.heroku.com/articles/procfile
