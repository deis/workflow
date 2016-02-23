# System Requirements

When deploying Deis, it's important to provision machines with adequate resources. Deis is a highly-available distributed system, which means that Deis components and your deployed applications will move around the cluster onto healthy hosts as hosts leave the cluster for various reasons (failures, reboots, autoscalers, etc.). Because of this, you should have ample spare resources on any machine in your cluster to withstand the additional load of running services for failed machines.

## Resources

Deis components consume approximately 2 - 2.5GB of memory across the cluster, and approximately 30GB of hard disk space. Because each machine should be able to absorb additional load should a machine fail, each machine must have:

* At least 4GB of RAM (more is better)
* At least 40GB of hard disk space

Note that these estimates are for Deis and Kubernetes only, and there should be ample room for deployed applications.

Running smaller machines will likely result in increased system load and has been known to result in component failures and other problems.

## Network

Due to changes introduced in Docker 1.3.1 related to insecure Docker registries, the hosts running Deis must be able to communicate via a private network procured by kubernetes in the `10.0.0.0/8` private address space. This allows the docker daemon used by the controller to communicate with the registry. Ensure that your hosts have the following entries in their respective DOCKER_OPTS:

	EXTRA_DOCKER_OPTS="--insecure-registry 10.0.0.0/8"
