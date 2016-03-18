# Platform Logging

**You must have the Daemon Sets api enabled for the logging system to work. To learn more visit [here](https://github.com/kubernetes/kubernetes/blob/master/docs/api.md#enabling-resources-in-the-extensions-group).**

## Description
The logging platform is made up of 2 components - [Fluentd](https://github.com/deis/fluentd) and [Logger](https://github.com/deis/logger).

[Fluentd](https://github.com/deis/fluentd) runs on every worker node of the cluster and is deployed as a [Daemons Set](http://kubernetes.io/v1.1/docs/admin/daemons.html). The Fluentd pods capture all of the stderr and stdout streams of every container running on the host (even those not hosted directly by kubernetes). It then sends this data via the Syslog UDP port (514) to the Logger component.

Logger acts like a syslog server and receives all log messages that are occurring on the cluster. It then filters this data to only Deis deploy applications and stores those log messages in a ring buffer where they can be fetched via the Deis CLI.

## Installation
Installation of the logging components is separate from the installation of the Deis platform because of the requirement of Daemon Sets. You will need to follow these steps to get the logging components running on your kubernetes cluster.

```
$ helm fetch deis/deis-logger
$ helm install deis-logger
```

You will then need to watch the components come up and verify they are in a running state by executing the following command:

```
$ kubectl get pods --namespace=deis
```

You should see output similar to this:
```
NAME                        READY     STATUS    RESTARTS   AGE
deis-builder-m68z9          1/1       Running   0          18h
deis-database-y765n         1/1       Running   0          1d
deis-logger-fluentd-pcndf   1/1       Running   0          20h
deis-logger-iwos5           1/1       Running   0          20h
deis-minio-zlmk8            1/1       Running   0          1d
deis-registry-bys9n         1/1       Running   0          1d
deis-router-h5f0i           1/1       Running   0          1d
deis-workflow-2v84b         1/1       Running   0          20h
```

There should be a fluentd pod per worker node of your Kubernetes cluster. So if you are running a 3 node cluster with 1 master and 2 workers you will have 2 fluentd pods running.

Once you have verified that the pods have started correctly you will need to restart your workflow pod so that it can capture the correct information about how to talk to the logger pod.

```
kubectl delete pod <deis-workflow-pod>
```

The replication controller will restart a new pod with all of the correct information.

Once the pod has restarted, you can verify the logging system is working by going to a deployed app and executing the `deis logs` command. If an error occurs the CLI will print a user friendly message about how to debug the issue.

```
Error: There are currently no log messages. Please check the following things:
1) Logger and fluentd pods are running.
2) If you just installed the logger components via the chart, please make sure you restarted the workflow pod.
3) The application is writing logs to the logger component.
You can verify that logs are appearing in the logger component by issuing the following command:
curl http://<log service ip>:8088/logs/myapp on a kubernetes host.
To get the service ip you can do the following: kubectl get svc deis-logger --namespace=deis
```

## Architecture Diagram
```
┌──────────────┐                            
│              │                            
│     Host     ├─────┐                      
│       Fluentd│     │                      
└──────────────┘   UDP                      
                     │                      
┌──────────────┐     │      ┌──────────────┐
│              │     │      │ Logger       │
│     Host     │─UDP─┼─────▶│     Host     │
│       Fluentd│     │      │ Fluentd      │
└──────────────┘     │      └──────────────┘
┌──────────────┐     │                      
│              │   UDP                      
│     Host     │─────┘                      
│       Fluentd│                            
└──────────────┘                            
```

## Default Configuration
By default the Fluentd pod can be configured to talk to numerous syslog endpoints. So for example it is possible to have Fluentd send log messages to both the Logger component and [Papertrail](https://papertrailapp.com/). This allows production deployments of Deis to satisfy stringent logging requirements such as offsite backups of log data.

Configuring Fluentd to talk to multiple syslog endpoints means adding the following stanzas to the Fluentd daemonset manifest -

```
env:
- name: "SYSLOG_HOST_1"
  value: $(DEIS_LOGGER_SERVICE_HOST)
- name: "SYSLOG_PORT_1"
  value: $(DEIS_LOGGER_SERVICE_PORT_TRANSPORT)
- name: "SYSLOG_HOST_2"
  value: "my.syslog.host.2"
- name: "SYSLOG_PORT_2"
  value: "5144"
  ....
- name: "SYSLOG_HOST_N"
  value: "my.syslog.host.n"
- name: "SYSLOG_PORT_N"
  value: "51333"
```

