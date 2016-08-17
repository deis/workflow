# Troubleshooting Applications

This document describes how one can troubleshoot common issues when deploying or debugging an
application that fails to start or deploy.


## Application has a Dockerfile, but a Buildpack Deployment Occurs

When you deploy an application to Workflow using `git push deis master` and the [Builder][]
attempts to deploy using the Buildpack workflow, check the following steps:

1. Are you deploying the correct project?
2. Are you pushing the correct git branch (`git push deis <branch>`)?
3. Is the `Dockerfile` in the project's root directory?
4. Have you committed the `Dockerfile` to the project?

## Application was Deployed, but is Failing to Start

If you deployed your application but it is failing to start, you can use `deis logs` to check
why the application fails to boot. Sometimes, the application container may fail to boot without
logging any information about the error. This typically occurs when the healthcheck configured for
the application fails. In this case, you can start by
[troubleshooting using kubectl][troubleshooting-kubectl]. You can inspect the application's current
state by examining the pod deployed in the application's namespace. To do that, run

	$ kubectl --namespace=myapp get pods
	NAME                          READY     STATUS                RESTARTS   AGE
	myapp-cmd-1585713350-3brbo    0/1       CrashLoopBackOff      2          43s

We can then describe the pod and determine why it is failing to boot:


	Events:
	  FirstSeen     LastSeen        Count   From                            SubobjectPath                           Type            Reason          Message
	  ---------     --------        -----   ----                            -------------                           --------        ------          -------
	  43s           43s             1       {default-scheduler }                                                    Normal          Scheduled       Successfully assigned myapp-cmd-1585713350-3brbo to kubernetes-node-1
	  41s           41s             1       {kubelet kubernetes-node-1}     spec.containers{myapp-cmd}              Normal          Created         Created container with docker id b86bd851a61f
	  41s           41s             1       {kubelet kubernetes-node-1}     spec.containers{myapp-cmd}              Normal          Started         Started container with docker id b86bd851a61f
	  37s           35s             1       {kubelet kubernetes-node-1}     spec.containers{myapp-cmd}              Warning         Unhealthy       Liveness probe failed: Get http://10.246.39.13:8000/healthz: dial tcp 10.246.39.13:8000: getsockopt: connection refused

In this instance, we set the healthcheck initial delay timeout for the application at 1 second,
which is too aggressive. The application needs some time to set up the API server after the
container has booted. By increasing the healthcheck initial delay timeout to 10 seconds, the
application is able to boot and is responding correctly.

See [Custom Health Checks][healthchecks] for more information on how to customize the application's
health checks to better suit the application's needs.


[builder]: ../understanding-workflow/components.md#builder-builder-slugbuilder-and-dockerbuilder
[healthchecks]: ../applications/managing-app-configuration.md#custom-health-checks
[troubleshooting-kubectl]: kubectl.md
