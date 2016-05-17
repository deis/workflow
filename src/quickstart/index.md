# Quick Start

Get started with Deis Workflow in three easy steps.

1. Install CLI tools for Helm Classic and Deis Workflow
2. Boot a Kubernetes and install Deis Workflow
3. Deploy your first application

This guide will help you set up a cluster suitable for evaluation, development and testing. When you are ready for staging and production, view our [production checklist](../managing-workflow/production-deployments.md).

## Step 1: Install CLI tools

For the quickstart we will [install both Helm Classic and Deis Workflow CLI](install-cli-tools.md).

## Step 2: Boot Kubernetes and Install Deis Workflow

There are many ways to boot and run Kubernetes. You may choose to get up and running in cloud environments or locally on
your laptop.

Cloud-based options:

* [Google Container Engine](provider/gke/boot.md): provides a managed Kubernetes environment, available with a few clicks.
* [Amazon Web Services](provider/aws/boot.md): uses Kubernetes upstream `kube-up.sh` to boot a cluster on AWS EC2.

If you would like to test on your local machine follow our guide for [Vagrant](provider/vagrant/boot.md).

If you have already created a Kubernetes cluster, check out the [system requirements](../installing-workflow/system-requirements.md) and then proceed to [installing Deis Workflow on your own Kubernetes clsuter](../installing-workflow/index.md).

## Step 3: Deploy your first app

Last but not least, [register a user and deploy your first application](deploy-an-app.md).
