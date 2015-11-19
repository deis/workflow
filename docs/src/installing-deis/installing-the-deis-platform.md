# Installing the Deis Platform

We will use the `deisctl` utility to provision the Deis platform from a CoreOS host or a workstation that has SSH access to CoreOS.

First check that you have `deisctl` installed and the version is correct.

    $ deisctl --version
    1.12.2

If not, follow instructions to [install deisctl][].

Ensure your SSH agent is running and select the private key that corresponds to the SSH key added
to your CoreOS nodes:

    $ eval `ssh-agent -s`
    $ ssh-add ~/.ssh/deis

!!! note
    For Vagrant clusters: `ssh-add ~/.vagrant.d/insecure_private_key`

Find the public IP address of one of your nodes, and export it to the DEISCTL_TUNNEL environment
variable (substituting your own IP address):

    $ export DEISCTL_TUNNEL=104.131.93.162

If you set up the "convenience" DNS records, you can just refer to them via

    $ export DEISCTL_TUNNEL="deis-1.example.com"

!!! note
    For Vagrant clusters: `export DEISCTL_TUNNEL=172.17.8.100`

This is the IP address where deisctl will attempt to communicate with the cluster. You can test
that it is working properly by running `deisctl list`. If you see a single line of output, the
control utility is communicating with the nodes.

Before provisioning the platform, we'll need to add the SSH key to Deis so it can connect to remote
hosts during `deis run`:

    $ deisctl config platform set sshPrivateKey=~/.ssh/deis

!!! note
    For Vagrant clusters: `deisctl config platform set sshPrivateKey=${HOME}/.vagrant.d/insecure_private_key`

We'll also need to tell the controller which domain name we are deploying applications under:

    $ deisctl config platform set domain=example.com

!!! note
    For Vagrant clusters: `deisctl config platform set domain=local3.deisapp.com`

Once finished, run this command to provision the Deis platform:

    $ deisctl install platform

You will see output like the following, which indicates that the units required to run Deis have
been loaded on the CoreOS cluster:

    ● ▴ ■
    ■ ● ▴ Installing Deis...
    ▴ ■ ●

    Scheduling data containers...
    ...
    Deis installed.
    Please run `deisctl start platform` to boot up Deis.

Run this command to start the Deis platform:

    $ deisctl start platform

Once you see "Deis started.", your Deis platform is running on a cluster! You may verify that all
of the Deis units are loaded and active by running the following command:

    $ deisctl list

All of the units should be active.

Now that you've finished provisioning a cluster, start [Using Deis][] to deploy your first application on Deis.

[install deisctl]: installing-deisctl.md
[helm]: http://helm.sh
[using deis]: ../using-deis/deploying-an-application.md
