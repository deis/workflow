# Booting Azure Container Service

## Prerequisites

1. Azure Accout - If you do not already have a Azure Cloud account, you can start a trial with $200 of free credit [here](https://azure.microsoft.com/en-us/free/). After completing sign up, you must add your billing information.
2. Some form of *nix-based terminal - MacOS, Ubuntu, CentOS, Bash on Windows, etc
<br>Where the following is present:
3. Azure CLI - The Azure CLI (2.0) provides the `az` command and allows you to interact with Azure through the command line. Install the CLI by following the instructions on [GitHub for the Azure CLI](https://github.com/Azure/azure-cli).
4. SSH Key - This is used to deploy the cluster. 
5. jq - to parse the JSON responses from the CLI. [jq download page](https://stedolan.github.io/jq/)

## Configure the Azure CLI

After installing the CLI, log in to your Azure Account by typing `az login` and output would look similar to this:
```
~ $ az login
To sign in, use a web browser to open the page https://aka.ms/devicelogin and enter the code F7DLMNOPE to authenticate.
[
  {
    "cloudName": "AzureCloud",
    "id": "57849302-a9f0-4908-b300-31337a0fb205",
    "isDefault": true,
    "name": "Azure Subscription",
    "state": "Enabled",
    "tenantId": "591acccc-dddd-4620-8f21-dbbeeeefee21",
    "user": {
      "name": "jhansen@deis.com",
      "type": "user"
    }
  }
]
```

Replace the value of SUBSCRIPTION_ID with the desired subscription id where you want to deploy from the previous step.  We also set the active subscription to deploy to.
```
SUBSCRIPTION_ID=57849302-a9f0-4908-b300-31337a0fb205
az account set --subscription="${SUBSCRIPTION_ID}"
```

## Create an Azure Service Principle

Next, create an Azure Service Principle that will be used to provision the ACS Kubernetes Cluster. Service Principles are entities that have permission to create resources on your behalf. New Service Principles must be given a unique name, a role, and an Azure subscription that the Service Principle may modify.

```
SP_JSON=`az ad sp create-for-rbac --role="Contributor" --scopes="/subscriptions/${SUBSCRIPTION_ID}"`
SP_NAME=`echo $SP_JSON | jq -r '.name'`
SP_PASS=`echo $SP_JSON | jq -r '.password'`
SP_TENANT=`echo $SP_JSON | jq -r '.tenant'`
echo SP_JSON
```

This should display an output similar to this.  jq has also automatically extracted these values for use in the creation of the cluster.
```
{
  "appId": "58b21231-3dd7-4546-bd37-9df88812331f",
  "name": "http://workflow-on-acs",
  "password": "349d4728-438a-52a5-ad25-a740aa0bd240",
  "tenant": "891a9ddc-477a-4620-8f21-db22ffd3ffea"
}
```

## Create Your ACS Kubernetes Cluster

You can build the Kubernetes cluster on ACS using primarily the Azure web Portal (UI) or entirely using the Azure command line (CLI).  Choose one of the two paths:

### Path 1: Azure 'az' CLI

1. Create an empty Azure resource group to deploy your cluster. The location of the resource group value can be changed to any datacenter.

```
RG_NAME=myresourcegroup
az resource group create --name "${RG_NAME}" --location southcentralus
```

2. Execute the command to deploy the cluster. The dns-prefix and ssh-key-value must be replaced with your own values.

```
  az acs create --resource-group="${RG_NAME}" --location="southcentralus" /
  --service-principal="${SP_NAME}" /
  --client-secret="${SP_PASS}" /
  --orchestrator-type=kubernetes --master-count=1 --agent-count=2 /
  --agent-vm-size="Standard_D2_v2" /
  --admin-username="k8sadmin" /
  --name="k8sanddeis" --dns-prefix="mydnsprefix" /
  --ssh-key-value @/home/myusername/.ssh/id_rsa.pub
```

### Path 2: UI

Sign into the [Azure Portal](https://portal.azure.com) and create a new Azure Container Service:

![](images/step1.png)

Select "Resource Manager" for the deployment model:

![](images/step2.png)

Provide basic settings for your Kubernetes cluster.

* User name: this is the unix user name that will be added to all master and worker nodes
* SSH public key: provide a public key that will be associated with the user name specified above
* Subscription: choose the Azure Subscription that will be charged for your compute resources
* Resource group: create a new resource group and give the group a unique name
* Location: choose an Azure location for your cluster

When you have filled out the information, click "Ok".

![](images/step3.png)

The next step takes the Service Principle name and password generated using the Azure CLI.

* Service Priciple Client ID: the name of the principle created above e.g. `http://workflow-on-acs`
* Service Priciple Client Secret: the password returned by the Azure CLI e.g. 349d4728-438a-52a5-ad25-a740aa0bd240

![](images/step4.png)

Next, configure the number of worker nodes, the node size, and DNS prefix for your cluster.

Worker nodes should have at least 7GB of available RAM.

Click "Ok" to continue.

![](images/step5.png)

Review the cluster configuration and click "Ok". After clicking "Purchase" on the next screen you will be returned to the Azure Portal dashboard.

![](images/step6.png)

The Kubernetes cluster will take a few minutes to complete provisioning and configure itself. To monitor the progress of the deployment select the "Resource Group" from the nav on the left, then select the cluster name:

![](images/step8.png)

![](images/step9.png)

## Connect to your Kubernetes Cluster

1. Find hostname for the master
2. SCP Kubeconfig from master into place
3. Set KUBECONFIG environment value

```
$ kubectl cluster-info
Kubernetes master is running at https://slack-acs-1mgmt.eastus.cloudapp.azure.com
Heapster is running at https://slack-acs-1mgmt.eastus.cloudapp.azure.com/api/v1/proxy/namespaces/kube-system/services/heapster
KubeDNS is running at https://slack-acs-1mgmt.eastus.cloudapp.azure.com/api/v1/proxy/namespaces/kube-system/services/kube-dns
kubernetes-dashboard is running at https://slack-acs-1mgmt.eastus.cloudapp.azure.com/api/v1/proxy/namespaces/kube-system/services/kubernetes-dashboard
```

You are now ready to [install Deis Workflow](install-azure-acs.md)
