## Register an Admin User

The first user to register against Deis Workflow will automatically be given administrative privileges.

If you installed Deis on GKE or AWS, Deis automatically creates a load balancer for the cluster. To get the IP of this load balancer, run `kubectl --namespace=deis describe svc deis-router`.

If you do not have an load balancer IP, the router automatically forwards traffic from a kubernetes node to the router. In this case, use the IP of a kubernetes node and the node
port that routes to port 80 on the controller.

Deis requires a wildcard DNS record to dynamically map app names to the router. Instead of setting up DNS records, this example will use `nip.io`. If your router IP is `1.1.1.1`, its url will be `1.1.1.1.nip.io`. The URL of the controller component will be `deis.1.1.1.1.nip.io`.

Use the controller url to register a user in the cluster.

```
$ deis register http://deis.104.197.125.75.nip.io
username: admin
password:
password (confirm):
email: jhansen@deis.com
Registered admin
Logged in as admin
$ deis whoami
You are admin at http://deis.104.197.125.75.nip.io
```

You have now registered your first user and you are ready to deploy an application.

## Deploy an Application

Deis Workflow supports three different types of applications, Buildpacks,
Dockerfiles and Docker Images. Our first application will be a simple Docker
Image-based application, so you don't have to wrestle with checking out code.

Run `deis create` to create a new application on Deis Workflow. If you do not
specify a name for your application, Workflow automatically generates a
friendly (and sometimes funny) name.

```
$ deis create --no-remote
Creating Application... done, created proper-barbecue
If you want to add a git remote for this app later, use `deis git:remote -a proper-barbecue`
```

Our application has been created and named `proper-barbecue`. As with the
`deis` hostname, any HTTP traffic to `proper-barbecue` will be automatically
routed to your application pods by the edge router.

Let's use the CLI to tell the platform to deploy an application and then use curl to send a request to the app:

```
$ deis pull deis/example-go -a proper-barbecue
Creating build... done
$ curl http://proper-barbecue.104.197.125.75.nip.io
Powered by Deis
```

!!! note
        If you see a 404 error, make sure you specified your application name with `-a <appname>`!

Workflow's edge router knows all about application names and automatically
sends traffic to the right application. The router sends traffic for
`proper-barbecue.104.197.125.75.nip.io` to your app, just like
`deis.104.197.125.75.nip.io` was sent to the Workflow API service.

## Change Application Configuration

Next, let's change some configuration using the CLI. Our example app is built
to read configuration from the environment. By using `deis config:set` we can
change how the application behaves:

```
$ deis config:set POWERED_BY="Docker Images + Kubernetes" -a proper-barbecue
Creating config... done

=== proper-barbecue Config
POWERED_BY      Docker Images + Kubernetes
```

Behind the scenes, Workflow creates a new release for your application and uses
Kubernetes to provide a zero-downtime rolling deploy to the new release!

Validate that our configuration change has worked:

```
$ curl http://proper-barbecue.104.197.125.75.nip.io
Powered by Docker Images + Kubernetes
```

## Scale Your Application

Last, let's scale our application by adding more application processes. Using the CLI you can easily add and remove
additional processes to service requests:

```
$ deis scale cmd=2 -a proper-barbecue
Scaling processes... but first, coffee!
done in 36s
=== proper-barbecue Processes
--- cmd:
proper-barbecue-v18-cmd-rk644 up (v18)
proper-barbecue-v18-cmd-0ag04 up (v18)
```

Congratulations! You have deployed, configured, and scaled your first application using Deis Workflow. 

## Going Further
There is a lot more you can do with Deis Workflow, play around with the CLI:

!!! important
    In order to have permission to push an app you must add a SSH key to your user on the Deis Workflow.
    For more information, please check [Users and SSH Keys](../users/ssh-keys/) and [Troubleshooting Workflow](../troubleshooting/).

* Roll back to a previous release with `deis rollback -a proper-barbecue`
* See application logs with `deis logs -a proper-barbecue`
* Try one of our other example applications like:
    * [deis/example-ruby-sinatra](https://github.com/deis/example-ruby-sinatra)
    * [deis/example-nodejs-express](https://github.com/deis/example-nodejs-express)
    * [deis/example-java-jetty](https://github.com/deis/example-java-jetty)
* Read about using application [Buildpacks](../applications/using-buildpacks) or [Dockerfiles](../applications/using-dockerfiles.md)
* Join our [#community slack channel](https://slack.deis.io) and meet the team!
