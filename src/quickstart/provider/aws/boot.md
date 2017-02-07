# Booting Kubernetes on Amazon Elastic Compute with kops

Amazon Elastic Compute Cloud (Amazon EC2) is a web service that provides compute capacity in the cloud. This quickstart
guide uses AWS EC2 to boot a Kubernetes cluster using [kubernetes kops](https://github.com/kubernetes/kops).


## Installing kops

Download the [latest](https://github.com/kubernetes/kops/releases/latest) version of kops


#### macOS

```bash
curl -sSL https://github.com/kubernetes/kops/releases/download/1.5.1/kops-darwin-amd64 -O
chmod +x kops-darwin-amd64
sudo mv kops-darwin-amd64 /usr/local/bin
```


#### linux

```bash
curl -sSL https://github.com/kubernetes/kops/releases/download/1.5.1/kops-linux-amd64 -O
chmod +x kops-darwin-amd64
sudo mv kops-darwin-amd64 /usr/local/bin
```

For more information see the official [kops installation guide](https://github.com/kubernetes/kops/blob/master/docs/aws.md)

## Validate kops is installed

```
kops version
Version 1.5.1
```

## Install kubectl if you haven't done so yet

```
curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/darwin/amd64/kubectl
chmod +x kubectl
sudo mv kubectl /usr/local/bin
```


## Setup your AWS account

#### Setup an IAM user for kops

In order to build clusters within AWS we'll create a dedicated IAM user for
`kops`.  This user requires API credentials in order to use `kops`.  Create
the user, and credentials, using the [AWS console](http://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSGettingStartedGuide/AWSCredentials.html).

The `kops` user will require the following IAM permissions to function properly:

 - AmazonEC2FullAccess
 - AmazonRoute53FullAccess
 - AmazonS3FullAccess
 - IAMFullAccess
 - AmazonVPCFullAccess

#### Create the IAM user from the command line

```bash
aws iam create-group --group-name kops

export arns="
arn:aws:iam::aws:policy/AmazonEC2FullAccess
arn:aws:iam::aws:policy/AmazonRoute53FullAccess
arn:aws:iam::aws:policy/AmazonS3FullAccess
arn:aws:iam::aws:policy/IAMFullAccess
arn:aws:iam::aws:policy/AmazonVPCFullAccess"

for arn in $arns; do aws iam attach-group-policy --policy-arn "$arn" --group-name kops; done

aws iam create-user --user-name kops-user

aws iam add-user-to-group --user-name kops-user --group-name kops

aws iam create-access-key --user-name kops-user
```

Note the *SecretAccessKey* and *AccessKeyID* so you can enter them in the following commands

```bash
aws configure # Input your credentials here
aws iam list-users
```


#### Configure DNS

In order to build a Kubernetes cluster with `kops`, we need to prepare
somewhere to build the required DNS records.  There are three scenarios
below and you should choose the one that most closely matches your AWS
situation.

#### Scenario 1a: A Domain purchased/hosted via AWS

If you bought your domain with AWS, then you should already have a hosted zone
in Route53.  If you plan to use this domain then no more work is needed.

In this example you own `example.com` and your records for Kubernetes would
look like `etcd-us-east-1c.internal.clustername.example.com`

You can now skip to [testing your DNS setup](#testing-your-dns-setup)

#### Scenario 1b: A subdomain under a domain purchased/hosted via AWS

In this scenario you want to contain all kubernetes records under a subdomain
of a domain you host in Route53.  This requires creating a second hosted zone
in route53, and then setting up route delegation to the new zone.

In this example you own `example.com` and your records for Kubernetes would
look like `etcd-us-east-1c.internal.clustername.kubernetes.example.com`

This is copying the NS servers of your **SUBDOMAIN** up to the **PARENT**
domain in Route53.  To do this you should:


```bash
ID=$(uuidgen) && aws route53 create-hosted-zone --name subdomain.example.com --caller-reference $ID | jq .DelegationSet.NameServers
```

* Note your **PARENT** hosted zone id

```bash
# Note: This example assumes you have jq installed locally.
aws route53 list-hosted-zones | jq '.HostedZones[] | select(.Name=="example.com.") | .Id'
```

* Create a new JSON file with your values (`subdomain.json`)

Note: The NS values here are for the **SUBDOMAIN**

```
{
  "Comment": "Create a subdomain NS record in the parent domain",
  "Changes": [
    {
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "subdomain.example.com",
        "Type": "NS",
        "TTL": 300,
        "ResourceRecords": [
          {
            "Value": "ns-1.awsdns-1.co.uk"
          },
          {
            "Value": "ns-2.awsdns-2.org"
          },
          {
            "Value": "ns-3.awsdns-3.com"
          },
          {
            "Value": "ns-4.awsdns-4.net"
          }
        ]
      }
    }
  ]
}
```

* Apply the **SUBDOMAIN** NS records to the **PARENT** hosted zone.

```
aws route53 change-resource-record-sets \
 --hosted-zone-id <parent-zone-id> \
 --change-batch file://subdomain.json
```

Now traffic to `*.example.com` will be routed to the correct subdomain hosted zone in Route53.

You can now skip to [testing your DNS setup](#testing-your-dns-setup)

#### Scenario 2: Setting up Route53 for a domain purchased with another registrar

If you bought your domain elsewhere, and would like to dedicate the entire domain to AWS you should follow the guide [here](http://docs.aws.amazon.com/Route53/latest/DeveloperGuide/domain-transfer-to-route-53.html)

You can now skip to [testing your DNS setup](#testing-your-dns-setup)

#### Scenario 3: Subdomain for clusters in route53, leaving the domain at another registrar

If you bought your domain elsewhere, but **only want to use a subdomain in AWS
Route53** you must modify your registrar's NS (NameServer) records.  We'll create
a hosted zone in Route53, and then migrate the subdomain's NS records to your
other registrar.

You might need to install [jq](https://github.com/stedolan/jq/wiki/Installation)
for some of these instructions.


```bash
ID=$(uuidgen) && aws route53 create-hosted-zone --name subdomain.kubernetes.com --caller-reference $ID | jq .DelegationSet.NameServers
```

* You will now go to your registrars page and log in. You will need to create a
  new **SUBDOMAIN**, and use the 4 NS records listed above for the new
  **SUBDOMAIN**. This **MUST** be done in order to use your cluster. Do **NOT**
  change your top level NS record, or you might take your site offline.

* Information on adding NS records with
  [Godaddy.com](https://www.godaddy.com/help/set-custom-nameservers-for-domains-registered-with-godaddy-12317)
* Information on adding NS records with [Google Cloud
  Platform](https://cloud.google.com/dns/update-name-servers)
  
 You can now skip to [testing your DNS setup](#testing-your-dns-setup)

#### Using Public/Private DNS (Kops 1.5+)

By default the assumption is that NS records are publically available.  If you
require private DNS records you should modify the commands we run later in this
guide to include:

```
kops create cluster --dns private $NAME
```

#### Testing your DNS setup

You should now able to dig your domain (or subdomain) and see the AWS Name
Servers on the other end.

```bash
dig ns subdomain.example.com
```

Should return something similar to:

```
;; ANSWER SECTION:
subdomain.example.com.        172800  IN  NS  ns-1.awsdns-1.net.
subdomain.example.com.        172800  IN  NS  ns-2.awsdns-2.org.
subdomain.example.com.        172800  IN  NS  ns-3.awsdns-3.com.
subdomain.example.com.        172800  IN  NS  ns-4.awsdns-4.co.uk.
```

This is a critical component of setting up clusters. If you are experiencing
problems with the Kubernetes API not coming up, chances are something is wrong
with the clusters DNS.

**Please DO NOT MOVE ON until you have validated your NS records!**


## Cluster State storage

In order to store the state of your cluster, and the representation of your
cluster, we need to create a dedicated S3 bucket for `kops` to use.  This
bucket will become the source of truth for our cluster configuration.  In
this guide we'll call this bucket `example-com-state-store`, but you should
add a custom prefix as bucket names need to be unique.

We recommend keeping the creation of this bucket confined to us-east-1,
otherwise more work will be required.

```bash
aws s3api create-bucket --bucket prefix-example-com-state-store --region us-east-1
```

Note: We **STRONGLY** recommend versioning your S3 bucket in case you ever need
to revert or recover a previous state store.

```bash
aws s3api put-bucket-versioning --bucket prefix-example-com-state-store  --versioning-configuration Status=Enabled
```


## Creating your first cluster

#### Prepare local environment

We're ready to start creating our first cluster!  Let's first setup a few
environment variables to make this process easier.

```bash
export NAME=myfirstcluster.example.com
export KOPS_STATE_STORE=s3://prefix-example-com-state-store
```

Note: You don’t have to use environmental variables here. You can always define
the values using the –name and –state flags later.

#### Create cluster configuration

We will need to note which availability zones are available to us. In this
example we will be deploying our cluster to the us-west-2 region.

```bash
aws ec2 describe-availability-zones --region us-west-2
```

Below is a basic create cluster command. The
below command will generate a cluster configuration, but not start building it.

```bash
kops create cluster \
    --zones us-west-2a \
    ${NAME}
```

All instances created by `kops` will be built within ASG (Auto Scaling Groups),
which means each instance will be automatically monitored and rebuilt by AWS if
it suffers any failure.

#### Customize Cluster Configuration

Now we have a cluster configuration, we can look at every aspect that defines
our cluster by editing the description.

```bash
kops edit cluster ${NAME}
```

This opens your editor (as defined by $EDITOR) and allows you to edit the
configuration.  The configuration is loaded from the S3 bucket we created
earlier, and automatically updated when we save and exit the editor.

We'll leave everything set to the defaults for now, but the rest of the `kops`
documentation covers additional settings and configuration you can enable.

#### Build the Cluster

Now we take the final step of actually building the cluster.  This'll take a
while.  Once it finishes you'll have to wait longer while the booted instances
finish downloading Kubernetes components and reach a "ready" state.

```bash
kops update cluster ${NAME} --yes
```

#### Use the Cluster

Remember when you installed `kubectl` earlier? The configuration for your
cluster was automatically generated and written to `~/.kube/config` for you!

A simple Kubernetes API call can be used to check if the API is online and
listening. Let's use `kubectl` to check the nodes.

```bash
kubectl get nodes
```

You will see a list of nodes that should match the `--zones` flag defined
earlier. This is a great sign that your Kubernetes cluster is online and
working.

Also `kops` ships with a handy validation tool that can be ran to ensure your
cluster is working as expected.

```bash
kops validate cluster
```

You can look at all the system components with the following command.

```
kubectl -n kube-system get po
```


You are now ready to [install Deis Workflow](install-aws.md)
