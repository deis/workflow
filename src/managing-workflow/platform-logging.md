# Platform Logging

The logging platform is made up of 2 components - [Fluentd](https://github.com/deis/fluentd) and [Logger](https://github.com/deis/logger).

[Fluentd](https://github.com/deis/fluentd) runs on every worker node of the cluster and is deployed as a [Daemon Set](http://kubernetes.io/v1.1/docs/admin/daemons.html). The Fluentd pods capture all of the stderr and stdout streams of every container running on the host (even those not hosted directly by kubernetes). Once the log message arrives in our [custom fluentd plugin](https://github.com/deis/fluentd/tree/master/rootfs/opt/fluentd/deis-output) we determine where the message originated.

If the message was from the [Workflow Controller](https://github.com/deis/controller) or from an application deployed via workflow we send it to the logs topic on the local [NSQD](nsq.io) instance.

If the message is from the [Workflow Router](https://github.com/deis/router) we build an Influxdb compatible message and send it to the same NSQD instance but instead place the message on the metrics topic.

Logger then acts as a consumer reading messages off of the NSQ logs topic storing those messages in a local Redis instance. When a user wants to retrieve log entries using the `deis logs` command we make an HTTP request from Controller to Logger which then fetches the appropriate data from Redis.

## Debugging Logger
If the `deis logs` command encounters an error it will return the following message:

```
Error: There are currently no log messages. Please check the following things:
1) Logger and fluentd pods are running.
2) The application is writing logs to the logger component by checking that an entry in the ring buffer was created: kubectl  --namespace=deis logs <logger pod>
3) Making sure that the container logs were mounted properly into the fluentd pod: kubectl --namespace=deis exec <fluentd pod> ls /var/log/containers
```

## Architecture Diagram
```
                        ┌────────┐                                        
                        │ Router │                  ┌────────┐     ┌─────┐
                        └────────┘                  │ Logger │◀───▶│Redis│
                            │                       └────────┘     └─────┘
                         Log file                       ▲                
                            │                           │                
                            ▼                           │                
┌────────┐             ┌─────────┐    logs/metrics   ┌─────┐             
│App Logs│──Log File──▶│ fluentd │───────topics─────▶│ NSQ │             
└────────┘             └─────────┘                   └─────┘             
                                                        │                
                                                        │                
┌─────────────┐                                         │                
│ HOST        │                                         ▼                
│  Telegraf   │───┐                                 ┌────────┐            
└─────────────┘   │                                 │Telegraf│            
                  │                                 └────────┘            
┌─────────────┐   │                                      │                
│ HOST        │   │    ┌───────────┐                     │                
│  Telegraf   │───┼───▶│ InfluxDB  │◀────Wire ───────────┘                
└─────────────┘   │    └───────────┘   Protocol                   
                  │          ▲                                    
┌─────────────┐   │          │                                    
│ HOST        │   │          ▼                                    
│  Telegraf   │───┘    ┌──────────┐                               
└─────────────┘        │ Grafana  │                               
                       └──────────┘                               
```

## Default Configuration
By default the Fluentd pod can be configured to talk to numerous syslog endpoints. So for example it is possible to have Fluentd send log messages to both the Logger component and [Papertrail](https://papertrailapp.com/). This allows production deployments of Deis to satisfy stringent logging requirements such as offsite backups of log data.

Configuring Fluentd to talk to multiple syslog endpoints means adding the following stanzas to the [Fluentd daemonset manifest](https://github.com/deis/charts/blob/master/workflow-v2.7.0/tpl/deis-logger-fluentd-daemon.yaml) -

```
env:
- name: "SYSLOG_HOST_1"
  value: "my.syslog.host"
- name: "SYSLOG_PORT_1"
  value: "5144"
  ....
- name: "SYSLOG_HOST_N"
  value: "my.syslog.host.n"
- name: "SYSLOG_PORT_N"
  value: "51333"
```

If you only need to talk to 1 Syslog endpoint you can use the following configuration within your chart:

```
env:
- name: "SYSLOG_HOST"
  value: "my.syslog.host"
- name: "SYSLOG_PORT"
  value: "5144"
```

### Customizing:
We currently support logging information to Syslog, Elastic Search, and Sumo Logic. However, we will gladly accept pull requests that add support to other locations. For more information please visit the [fluentd repository](https://github.com/deis/fluentd).
