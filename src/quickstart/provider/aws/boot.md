# Booting Kubernetes on Amazon Elastic Compute

Amazon Elastic Compute Cloud (Amazon EC2) is a web service that provides compute capacity in the cloud. This quickstart
guide uses AWS EC2 to boot a Kubernetes cluster using the open source provisioning scripts.

## Pre-requisites

1. You need an active AWS account. Visit [AWS portal](http://aws.amazon.com) to sign up
2. You need AWS API keys with full access
3. Install the AWS cli tools, you can find instructions for your platform at [AWS Command Line Interface Site](https://aws.amazon.com/cli/)

To verify that your CLI is configured properly, run `aws ec2 describe-regions`:

```
$ aws ec2 describe-regions --output=text
REGIONS	ec2.eu-west-1.amazonaws.com	eu-west-1
REGIONS	ec2.ap-southeast-1.amazonaws.com	ap-southeast-1
REGIONS	ec2.ap-southeast-2.amazonaws.com	ap-southeast-2
REGIONS	ec2.eu-central-1.amazonaws.com	eu-central-1
REGIONS	ec2.ap-northeast-2.amazonaws.com	ap-northeast-2
REGIONS	ec2.ap-northeast-1.amazonaws.com	ap-northeast-1
REGIONS	ec2.us-east-1.amazonaws.com	us-east-1
REGIONS	ec2.sa-east-1.amazonaws.com	sa-east-1
REGIONS	ec2.us-west-1.amazonaws.com	us-west-1
REGIONS	ec2.us-west-2.amazonaws.com	us-west-2
```

## Download and Unpack Kubernetes

First, make a directory to hold the Kubernetes release files:

```
$ mkdir my-first-cluster
$ cd my-first-cluster
```

See [Kubernetes Versions](https://deis.com/docs/workflow/installing-workflow/system-requirements/#kubernetes-versions) under System Requirements and download a Kubernetes release that is compatible with Deis Workflow, and extract the archive on your machine.

This archive has everything that you need to launch Kubernetes. It's a fairly large archive, so it may take some time to download:

```
$ curl -sSL https://storage.googleapis.com/kubernetes-release/release/v1.3.5/kubernetes.tar.gz -O
$ tar -xvzf kubernetes.tar.gz
$ cd kubernetes
$ ls
LICENSES     README.md    Vagrantfile  cluster/     contrib/     docs/        examples/    platforms/   server/      third_party/ version
```

## Configure the Kubernetes Environment

Before calling the Kubernetes setup scripts, we need to change a few defaults so that Deis Workflow works best. Type
each of these commands into your terminal application before calling `kube-up.sh`.

Next, pick the AWS Availability Zone you would like to use. The boot script will create a new VPC in that region.

```
export KUBE_AWS_ZONE=us-west-1c
export KUBERNETES_PROVIDER=aws
```

For evaluation, we find that the t2 instance classes are a reasonable bang for the buck. Do note that the t2 class does
track CPU credits. Performance of your evaluation cluster may be impacted when you exhaust the CPU credit limit. Select
your instance sizes and worker count.

```
export MASTER_SIZE=t2.medium
export NODE_SIZE=t2.large
export NUM_NODES=2
export NODE_ROOT_DISK_SIZE=100
```

Last, so you can easily identify instances in the AWS Console, specify an instance prefix:
```
export INSTANCE_PREFIX=first-k8s
```

## Setup kubectl CLI

Very soon, we will need to use `kubectl` to check everything is running smoothly and
for that let's get it on the $PATH.

For Mac OS, run:

    $ ln -fs $PWD/platforms/darwin/amd64/kubectl /usr/local/bin/kubectl

For Linux, use this instead:

    $ sudo ln -fs $PWD/platforms/linux/amd64/kubectl /usr/local/bin/kubectl

!!! note
    If you are using any other architecture, you can look at the `platforms/<os>/<arch>`
    tree to see all the available binaries

## Boot Your First Cluster

We are now ready to boot our first Kubernetes cluster on AWS!

Since this script does a **lot** of stuff, we'll break it into sections.

```
$ ./cluster/kube-up.sh
Creating a kubernetes on aws...
... Starting cluster in us-west-1c using provider aws
... calling verify-prereqs
... calling kube-up
Starting cluster using os distro: jessie
Uploading to Amazon S3
+++ Staging server tars to S3 Storage: kubernetes-staging-52e3410afddda7a4600f10ee5b1e43fb/devel
upload:
Uploaded server tars:
  SERVER_BINARY_TAR_URL: ...
  SALT_TAR_URL: ...
  BOOTSTRAP_SCRIPT_URL: ...
```

Here, we have downloaded the Kubernetes release archive and started the process of cluster provisioning. Release
artifacts are automatically pushed to S3 for use by machines as they are provisioned.

```
Using SSH key with (AWS) fingerprint: 32:5b:38:76:e6:e8:6e:ae:98:5d:8c:1f:3b:4e:8d:6c
Creating vpc.
Using VPC vpc-11672d74
Using DHCP option set dopt-d78907b2
Creating subnet.
Using subnet subnet-2b632072
Creating Internet Gateway.
Using Internet Gateway igw-2943f94c
Associating route table.
Creating route table
Associating route table rtb-0cc5eb69 to subnet subnet-2b632072
Adding route to route table rtb-0cc5eb69
Using Route Table rtb-0cc5eb69
Creating master security group.
Creating security group kubernetes-master-kubernetes.
Creating minion security group.
Creating security group kubernetes-minion-kubernetes.
Using master security group: kubernetes-master-kubernetes sg-a3bf1cc7
Using minion security group: kubernetes-minion-kubernetes sg-acbf1cc8
Creating master disk: size 20GB, type gp2
Allocated Elastic IP for master: 52.9.206.49
Generating certs for alternate-names: IP:52.9.206.49,IP:172.20.0.9,IP:10.0.0.1,DNS:kubernetes,DNS:kubernetes.default,DNS:kubernetes.default.svc,DNS:kubernetes.default.svc.cluster.local,DNS:kubernetes-master
```

Next, the VPC is provisioned with all of the necessary bits including security groups, route tables, subnets and
internet gateways.

```
Starting Master
Waiting for master to be ready
Attempt 1 to check for master nodeWaiting for instance i-629517d7 to be running (currently pending)
Sleeping for 3 seconds...
Waiting for instance i-629517d7 to be running (currently pending)
Sleeping for 3 seconds...
 [master running]
Attaching IP 52.9.206.49 to instance i-629517d7
Attaching persistent data volume (vol-1e605fa3) to master
2016-05-11T23:15:38.845Z	/dev/sdb	i-629517d7	attaching	vol-1e605fa3
```

Now that the master instance has booted, the script automatically configures your `kubectl` tool with appropriate
authentication and endpoint information.

```
cluster "aws_kubernetes" set.
user "aws_kubernetes" set.
context "aws_kubernetes" set.
switched to context "aws_kubernetes".
user "aws_kubernetes-basic-auth" set.
Wrote config for aws_kubernetes to /Users/jhansen/.kube/config
```

Up next, worker nodes are provisioned by an auto-scaling group, and we wait for those nodes to come up.

```
Creating minion configuration
Creating autoscaling group
 0 minions started; waiting
 0 minions started; waiting
 0 minions started; waiting
 0 minions started; waiting
 1 minions started; waiting
 1 minions started; waiting
 1 minions started; waiting
 2 minions started; ready
Waiting for cluster initialization.

  This will continually check to see if the API for kubernetes is reachable.
  This might loop forever if there was some uncaught error during start
  up.
Waiting for cluster initialization.

  This will continually check to see if the API for kubernetes is reachable.
  This might loop forever if there was some uncaught error during start
  up.

.................................................................................................................Kubernetes cluster created.
Sanity checking cluster...
Attempt 1 to check Docker on node @ 52.53.207.230 ...working
Attempt 1 to check Docker on node @ 52.53.172.73 ...working
```

After these nodes come up, you are almost ready to go!

```
Kubernetes cluster is running.  The master is running at:

  https://52.9.206.49

The user name and password to use is located in /Users/jhansen/.kube/config.

... calling validate-cluster
Waiting for 2 ready nodes. 0 ready nodes, 1 registered. Retrying.
Waiting for 2 ready nodes. 0 ready nodes, 1 registered. Retrying.
Waiting for 2 ready nodes. 0 ready nodes, 1 registered. Retrying.
Waiting for 2 ready nodes. 1 ready nodes, 1 registered. Retrying.
Waiting for 2 ready nodes. 1 ready nodes, 2 registered. Retrying.
Waiting for 2 ready nodes. 1 ready nodes, 2 registered. Retrying.
Found 2 node(s).
NAME                                         STATUS    AGE
ip-172-20-0-192.us-west-1.compute.internal   Ready     36s
ip-172-20-0-193.us-west-1.compute.internal   Ready     1m
Flag --api-version has been deprecated, flag is no longer respected and will be deleted in the next release
Validate output:
NAME                 STATUS    MESSAGE              ERROR
scheduler            Healthy   ok
controller-manager   Healthy   ok
etcd-0               Healthy   {"health": "true"}
etcd-1               Healthy   {"health": "true"}
Cluster validation succeeded
Done, listing cluster services:

Kubernetes master is running at https://52.9.206.49
Elasticsearch is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/elasticsearch-logging
Heapster is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/heapster
Kibana is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/kibana-logging
KubeDNS is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/kube-dns
kubernetes-dashboard is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/kubernetes-dashboard
Grafana is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/monitoring-grafana
InfluxDB is running at https://52.9.206.49/api/v1/proxy/namespaces/kube-system/services/monitoring-influxdb

Kubernetes binaries at /Users/jhansen/p/docs/kubernetes/cluster/
You may want to add this directory to your PATH in $HOME/.profile
Installation successful!
```

## Items of note!

A few things to note! Your Kubernetes master is now up and running and we are ready to install Deis Workflow. If you
need to access the Kubernetes master the default username is `admin` and the ssh key lives at `~/.ssh/kube_aws_rsa`.

```
$ ssh -i ~/.ssh/kube_aws_rsa admin@52.9.206.49

Welcome to Kubernetes v1.2.4!

You can find documentation for Kubernetes at:
  http://docs.kubernetes.io/

You can download the build image for this release at:
  https://storage.googleapis.com/kubernetes-release/release/v1.2.4/kubernetes-src.tar.gz

It is based on the Kubernetes source at:
  https://github.com/kubernetes/kubernetes/tree/v1.2.4

For Kubernetes copyright and licensing information, see:
  /usr/local/share/doc/kubernetes/LICENSES

admin@ip-172-20-0-9:~$
```

When you are finished with the Kubernetes cluster, you may terminate the AWS resources by running
`./cluster/kube-down.sh`. If you are using a new shell environment you will need to set the environment variables we
used above so `kube-down.sh` can find the right cluster.

You are now ready to [install Deis Workflow](install-aws.md)
