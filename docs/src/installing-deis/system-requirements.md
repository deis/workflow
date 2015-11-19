# System Requirements

When deploying Deis, it's important to provision machines with adequate resources. Deis is a highly-available distributed system, which means that Deis components and your deployed applications will move around the cluster onto healthy hosts as hosts leave the cluster for various reasons (failures, reboots, autoscalers, etc.). Because of this, you should have ample spare resources on any machine in your cluster to withstand the additional load of running services for failed machines.

## Resources

Deis components consume approximately 2 - 2.5GB of memory across the cluster, and approximately 30GB of hard disk space. Because each machine should be able to absorb additional load should a machine fail, each machine must have:

* At least 4GB of RAM (more is better)
* At least 40GB of hard disk space

Note that these estimates are for Deis and CoreOS only, and there should be ample room for deployed applications.

Running smaller machines will likely result in increased system load and has been known to result in component failures, issues with etcd/fleet, and other problems.

## Cluster Size

For the [Scheduler][] and the [Store][] components to work properly, clusters must have at least three nodes. The etcd service must always be able to obtain a quorum, and the Ceph data store must maintain at least three replicas of persistent data.

If running multiple (at least three) machines of an adequate size is unreasonable, it is recommended to investigate the [Dokku][] project instead. Dokku is [sponsored][] by Deis and is ideal for environments where a highly-available distributed system is not necessary (i.e. local development, testing, etc.).

## Network

Due to changes introduced in Docker 1.3.1 related to insecure Docker registries, the hosts running Deis must be able to communicate via a private network in one of the RFC 1918 or RFC 6598 private address spaces: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, or `100.64.0.0/10`.


[dokku]: https://github.com/progrium/dokku
[scheduler]: ../reference-guide/terms.md#scheduler
[sponsored]: http://deis.io/deis-sponsors-dokku/
[store]: ../understanding-deis/components.md#store
