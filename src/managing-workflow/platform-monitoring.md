# Platform Monitoring

## Description

We now include a monitoring stack for introspection on a running Kubernetes cluster. The stack includes 3 components:

* [Telegraf](https://docs.influxdata.com/telegraf) - Metrics collection daemon written by team behind InfluxDB.
* [InfluxDB](https://docs.influxdata.com/influxdb) - Time series database
* [Grafana](http://grafana.org/) - Graphing tool for time series data

## Architecture Diagram

```
                        ┌────────┐                                        
                        │ Router │                  ┌────────┐     ┌─────┐
                        └────────┘                  │ Logger │◀───▶│Redis│
                            │                       └────────┘     └─────┘
                        Log file                        ▲                
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

## [Grafana](https://grafana.com/)
Grafana allows users to create custom dashboards that visualize the data captured to the running InfluxDB component. By default Grafana is exposed using a [service annotation](https://github.com/deis/router#how-it-works) through the router at the following URL: `http://grafana.mydomain.com`. The default login is `admin/admin`. If you are interested in changing these values please see [Tuning Component Settings][].

Grafana will preload several dashboards to help operators get started with monitoring Kubernetes and Deis Workflow.
These dashboards are meant as starting points and don't include every item that might be desirable to monitor in a
production installation.

Deis Workflow monitoring by default does not write data to the host filesystem or to long-term storage. If the Grafana instance fails, modified dashboards are lost.

### Production Configuration
A production install of Grafana should have the following configuration values changed if possible:

* Change the default username and password from `admin/admin`. The value for the password is passed in plain text so it is best to set this value on the command line instead of checking it into version control.
* Enable persistence
* Use a supported external database such as mysql or postgres. You can find more information [here](https://github.com/deis/monitor/blob/master/grafana/rootfs/usr/share/grafana/grafana.ini.tpl#L62)


### On Cluster Persistence
Enabling persistence will allow your custom configuration to persist across pod restarts. This means that the default sqllite database (which stores things like sessions and user data) will not disappear if you upgrade the Workflow installation. 

If you wish to have persistence for Grafana you can set `enabled` to `true` in the `values.yaml` file before running `helm install`.

```
 grafana:
   # Configure the following ONLY if you want persistence for on-cluster grafana
   # GCP PDs and EBS volumes are supported only
   persistence:
     enabled: true # Set to true to enable persistence
     size: 5Gi # PVC size
```

### Off Cluster Grafana

If you wish to provide your own Grafana instance you can set `grafana_location` in the `values.yaml` file before running `helm install`.

## [InfluxDB](https://docs.influxdata.com/influxdb)
InfluxDB writes data to the host disk; however, if the InfluxDB pod dies and comes back on another host, the data will not be recovered. The InfluxDB Admin UI is also exposed through the router allowing users to access the query engine by going to `influx.mydomain.com`. You will need to configure where to find the `influx-api` endpoint by clicking the "gear" icon at the top right and changing the host to `influxapi.mydomain.com` and port to `80`.

### On Cluster Persistence
If you wish to have persistence for InfluxDB you can set `enabled` to `true` in the `values.yaml` file before running `helm install`.

```
 influxdb:
   # Configure the following ONLY if you want persistence for on-cluster grafana
   # GCP PDs and EBS volumes are supported only
   persistence:
     enabled: true # Set to true to enable persistence
     size: 5Gi # PVC size
```

### Off Cluster Influxdb

To use off-cluster Influx, please provide the following values in the `values.yaml` file before running `helm install`.

* `influxdb_location=off-cluster`
* `url = "http://my-influxhost.com:8086"`
* `database = "metrics"`
* `user = "InfluxUser"`
* `password = "MysuperSecurePassword"`


## [Telegraf](https://docs.influxdata.com/telegraf)

Telegraf is the metrics collection daemon used within the monitoring stack. It will collect and send the following metrics to InfluxDB:

* System level metrics such as CPU, Load Average, Memory, Disk, and Network stats
* Container level metrics such as CPU and Memory
* Kubernetes metrics such as API request latency, Pod Startup Latency, and number of running pods

It is possible to send these metrics to other endpoints besides InfluxDB. For more information please consult the following [file](https://github.com/deis/monitor/blob/master/telegraf/rootfs/config.toml.tpl)

### Customizing the Monitoring Stack

To learn more about customizing each of the above components please visit the [Tuning Component Settings][] section.

[Tuning Component Settings]: tuning-component-settings.md#customizing-the-monitor