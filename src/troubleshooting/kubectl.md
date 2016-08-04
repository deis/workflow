# Troubleshooting using Kubectl

This document describes how one can use `kubectl` to debug any issues with the cluster.

## Diving into the Components

Using `kubectl`, one can inspect the cluster's current state. When `helmc install workflow-v2.3.0`
is invoked, Workflow is installed into the `deis` namespace. To inspect if Workflow is running,
run:

	$ kubectl --namespace=deis get pods
	NAME                          READY     STATUS              RESTARTS   AGE
	deis-builder-gqum7            0/1       ContainerCreating   0          4s
	deis-controller-h6lk6         0/1       ContainerCreating   0          4s
	deis-database-56v39           0/1       ContainerCreating   0          4s
	deis-logger-fluentd-xihr1     0/1       Pending             0          2s
	deis-logger-grupg             0/1       ContainerCreating   0          3s
	deis-minio-c2exb              0/1       Pending             0          3s
	deis-monitor-grafana-9ccur    0/1       Pending             0          3s
	deis-monitor-influxdb-f9ftm   0/1       Pending             0          3s
	deis-monitor-stdout-novxs     0/1       Pending             0          3s
	deis-monitor-telegraf-dc3y3   0/1       Pending             0          2s
	deis-registry-5bor6           0/1       Pending             0          3s
	deis-router-r02sd             0/1       Pending             0          2s
	deis-workflow-manager-hizv6   0/1       Pending             0          2s

!!! tip
	To save precious keystrokes, alias `kubectl --namespace=deis` to `kd` so it is easier to type
	in the future.

To fetch the logs of a specific component, use `kubectl logs`:

	$ kubectl --namespace=deis logs deis-controller-h6lk6
	system information:
	Django Version: 1.9.6
	Python 3.5.1
	addgroup: gid '0' in use
	Django checks:
	System check identified no issues (2 silenced).
	[...]

To dive into a running container to inspect its environment, use `kubectl exec`:

	$ kubectl --namespace=deis exec -it deis-database-56v39 gosu postgres psql
	psql (9.4.7)
	Type "help" for help.

	postgres=# \l
	                                                List of databases
	               Name               |  Owner   | Encoding |  Collate   |   Ctype    |   Access privileges
	----------------------------------+----------+----------+------------+------------+-----------------------
	 V7wckOHIAn3MZ7mO5du4q5IRq7yib1Oc | postgres | UTF8     | en_US.utf8 | en_US.utf8 |
	 postgres                         | postgres | UTF8     | en_US.utf8 | en_US.utf8 |
	 template0                        | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
	                                  |          |          |            |            | postgres=CTc/postgres
	 template1                        | postgres | UTF8     | en_US.utf8 | en_US.utf8 | =c/postgres          +
	                                  |          |          |            |            | postgres=CTc/postgres
	(4 rows)
	postgres=# \connect V7wckOHIAn3MZ7mO5du4q5IRq7yib1Oc
	You are now connected to database "V7wckOHIAn3MZ7mO5du4q5IRq7yib1Oc" as user "postgres".
	V7wckOHIAn3MZ7mO5du4q5IRq7yib1Oc=# \dt
	                                 List of relations
	 Schema |              Name              | Type  |              Owner
	--------+--------------------------------+-------+----------------------------------
	 public | api_app                        | table | V7wckOHIAn3MZ7mO5du4q5IRq7yib1Oc
	 public | api_build                      | table | V7wckOHIAn3MZ7mO5du4q5IRq7yib1Oc
	 public | api_certificate                | table | V7wckOHIAn3MZ7mO5du4q5IRq7yib1Oc
	 public | api_config                     | table | V7wckOHIAn3MZ7mO5du4q5IRq7yib1Oc
	 public | api_domain                     | table | V7wckOHIAn3MZ7mO5du4q5IRq7yib1Oc
	 public | api_key                        | table | V7wckOHIAn3MZ7mO5du4q5IRq7yib1Oc
	 public | api_push                       | table | V7wckOHIAn3MZ7mO5du4q5IRq7yib1Oc
	 public | api_release                    | table | V7wckOHIAn3MZ7mO5du4q5IRq7yib1Oc
	 public | auth_group                     | table | V7wckOHIAn3MZ7mO5du4q5IRq7yib1Oc
	 --More--
	 V7wckOHIAn3MZ7mO5du4q5IRq7yib1Oc=# SELECT COUNT(*) from api_app;
	 count
	-------
	     0
	(1 row)
