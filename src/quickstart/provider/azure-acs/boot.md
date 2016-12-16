# Booting Azure Container Service

## Prerequisites

1. Azure Account - An active Azure Cloud account is required for this quick start. Start a trial with $200 of free credit [here](https://azure.microsoft.com/en-us/free/). After completing trial sign up, a credit card for billing must be added, but will not be charged.

2. Some form of *nix-based terminal - MacOS, Ubuntu, CentOS, Bash on Windows, etc
<br>Where the following is present:

3. Azure CLI - The Azure CLI (2.0) provides the `az` command which drives Azure through the command line. Install the CLI by following the instructions on [GitHub for the Azure CLI](https://github.com/Azure/azure-cli).

4. SSH Key - This is used to deploy the cluster. [This URL helps to create SSH keys compatible with Linux VMs on Azure](https://docs.microsoft.com/azure/virtual-machines/virtual-machines-linux-mac-create-ssh-keys)

5. jq - to parse the JSON responses from the CLI. [jq download page](https://stedolan.github.io/jq/)

## Configure the Azure CLI

After installing the CLI, log in to an Azure Account by typing `az login`. Take the code offered, enter it into the text box at [https://aka.ms/devicelogin](https://aka.ms/devicelogin), and login using an Azure account which has ownership or contributor permissions over at least one subscription.

> Note: If the Azure subscription is configured for 2FA (not done by default), the Azure account used to login must have ownership credentials to create the service principal.

```
$ az login
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

The `id` field from the `az login` command is the Azure Subscription Id. This id will be used throughout the guide. As a matter of convenience, set an environment variable named `SUBSCRIPTION_ID` with the value of the id (e.g. 57849302-a9f0-4908-b300-31337a0fb205). Check the configuration by setting the active subscription with `az account set`:
```
$ export SUBSCRIPTION_ID=57849302-a9f0-4908-b300-31337a0fb205
$ az account set --subscription="${SUBSCRIPTION_ID}"
```

## Create an Azure Service Principal

Next, create an Azure Service Principal that will be used to provision the ACS Kubernetes Cluster. Service Principals are entities that have permission to create resources in an Azure Subscription. New Service Principals must be given a unique name, a role, and an Azure subscription that the Service Principal may modify.

```
$ export SP_JSON=`az ad sp create-for-rbac -n="http://acsk8sdeis" --role="Contributor" --scopes="/subscriptions/${SUBSCRIPTION_ID}"`
$ export SP_NAME=`echo $SP_JSON | jq -r '.name'`
$ export SP_PASS=`echo $SP_JSON | jq -r '.password'`
$ echo $SP_JSON
```

This should display an output similar to this. `jq` has also automatically extracted these values for use in the creation of the cluster.
```
{
  "appId": "58b21231-3dd7-4546-bd37-9df88812331f",
  "name": "http://workflow-on-acs",
  "password": "349d4728-438a-52a5-ad25-a740aa0bd240",
  "tenant": "891a9ddc-477a-4620-8f21-db22ffd3ffea"
}
```

## Create an ACS Kubernetes Cluster

Azure supports two methods to build an ACS Kubernetes cluster, through the Azure Web Portal (UI) or using the Azure command line (CLI).  Choose one of the two paths:

### Path 1: Azure 'az' CLI

Create an empty Azure resource group to hold the ACS Kubernetes cluster. The location of the resource group can be set to any available Azure datacenter. To see the possible locations run `az account list-locations --query [].name --output tsv`

Create an environment variable to hold the resource group name:

```
$ export RG_NAME=myresourcegroup
$ az group create --name "${RG_NAME}" --location southcentralus
```

Execute the command to deploy the cluster. The `dns-prefix` and `ssh-key-value` must be replaced with your own values.

```
$ az acs create --resource-group="${RG_NAME}" --location="southcentralus" \
  --service-principal="${SP_NAME}" \
  --client-secret="${SP_PASS}" \
  --orchestrator-type=kubernetes --master-count=1 --agent-count=2 \
  --agent-vm-size="Standard_D2_v2" \
  --admin-username="k8sadmin" \
  --name="k8sanddeis" --dns-prefix="mydnsprefix" \
  --ssh-key-value @/home/myusername/.ssh/id_rsa.pub
```

> Note: When `az acs create` starts, the provisioning process runs entirely silent in the background. After a few minutes the `az` command should return with information about the deployment created as shown below.

```
{
  "id": "/subscriptions/ed7cedf5-fcd8-4a5d-9980-96d838f65ab8/resourceGroups/myresourcegroup/providers/Microsoft.Resources/deployments/azurecli1481240849.890798",
  "name": "azurecli1481240849.890798",
  "properties": {
    "correlationId": "61be22d1-28d8-466c-a2ba-7bc11c2a3578",
    "debugSetting": null,
    "dependencies": [],
    "mode": "Incremental",
    "outputs": null,
    "parameters": null,
    "parametersLink": null,
    "providers": [
      {
        "id": null,
        "namespace": "Microsoft.ContainerService",
 ...
  },
  "resourceGroup": "myresourcegroup"
}
```

### Path 2: UI

Sign into the [Azure Portal](https://portal.azure.com) and create a new Azure Container Service:

![](images/step1.png)

Select "Resource Manager" for the deployment model:

![](images/step2.png)

Provide basic settings for the new ACS Kubernetes cluster.

* User name: this is the unix user name that will be added to all master and worker nodes
* SSH public key: provide a public key that will be associated with the user name specified above
* Subscription: choose the Azure Subscription that will be charged for the compute resources
* Resource group: create a new resource group and give the group a unique name
* Location: choose an Azure location for the cluster

When the required information is filled out, click "Ok".

![](images/step3.png)

The next step takes the Service Principal name and password generated using the Azure CLI.

* Service Principal Client ID: the name of the principal created above e.g. `http://workflow-on-acs`
* Service Principal Client Secret: the password returned by the Azure CLI e.g. 349d4728-438a-52a5-ad25-a740aa0bd240

![](images/step4.png)

Next, configure the number of worker nodes, the node size, and DNS prefix for the cluster.

Worker nodes should have at least 7GB of available RAM.

Click "Ok" to continue.

![](images/step5.png)

Review the cluster configuration and click "Ok". After clicking "Purchase" on the next screen the browser will be returned to the Azure Portal dashboard.

![](images/step6.png)

The Kubernetes cluster will take a few minutes to complete provisioning and configure itself. To monitor the progress of the deployment select the "Resource Group" from the nav on the left, then select the cluster name:

![](images/step8.png)

![](images/step9.png)

## Connect to the ACS Kubernetes Cluster

Retrieve the fully qualified domain name (FQDN) for the Kubernetes master.

```
$ export K8S_FQDN=`az acs list -g $RG_NAME --query [0].masterProfile.fqdn --output tsv`
$ echo $K8S_FQDN
```

Download the Kubeconfig from the master to the local machine, make sure to use the same SSH credentials used to create the cluster:

```
$ scp -i ~/.ssh/id_rsa k8sadmin@$K8S_FQDN:.kube/config ~/.kube/k8sanddeis.config
The authenticity of host 'mydnsprefix.myregion.cloudapp.azure.com (40.78.71.181)' can't be established.
ECDSA key fingerprint is a0:09:ff:59:83:47:70:38:d4:0d:68:b2:cf:0f:2a:cf.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added 'mydnsprefix.myregion.cloudapp.azure.com,40.78.71.181' (ECDSA) to the list of known hosts.
```

Point `kubectl` at the kubernetes configuration file by setting the `KUBECONFIG` environment value:

```
export KUBECONFIG=~/.kube/k8sanddeis.config
```

Verify connectivity to the new ACS Kubernetes cluster by running `kubectl cluster-info`

```
$ kubectl cluster-info
Kubernetes master is running at https://mydnsprefix.myregion.cloudapp.azure.com
Heapster is running at https://mydnsprefix.myregion.cloudapp.azure.com/api/v1/proxy/namespaces/kube-system/services/heapster
KubeDNS is running at https://mydnsprefix.myregion.cloudapp.azure.com/api/v1/proxy/namespaces/kube-system/services/kube-dns
kubernetes-dashboard is running at https://mydnsprefix.myregion.cloudapp.azure.com/api/v1/proxy/namespaces/kube-system/services/kubernetes-dashboard
```

You are now ready to [install Deis Workflow](install-azure-acs.md)
