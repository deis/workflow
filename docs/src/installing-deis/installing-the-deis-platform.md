# Installing the Deis Platform

We will use the `helm` utility to provision the Deis platform to a kubernetes cluster. If you don't
have `helm` installed, see [installing helm][helm] for more info.

First check that you have `helm` installed and the version is correct.

    $ helm --version
    0.2.0

Ensure your kubectl client is installed and ensure it can connect to your kubernetes cluster. This
is where `helm` will attempt to communicate with the cluster. You can test that it is working
properly by running `kubectl get nodes`. If you see a list of available nodes, kubectl is
communicating with the kubernetes master.

Once finished, run this command to provision the Deis platform:

    $ helm repo add deis https://github.com/deis/charts
    $ helm install deis/deis

You can then monitor their status by running

```
$ kubectl get pods --namespace=deis
```

Once you see all of the pods ready, your Deis platform is running on a cluster!

Now that you've finished provisioning a cluster, start [Using Deis][] to deploy your first
application on Deis.

[install deisctl]: installing-deisctl.md
[helm]: http://helm.sh
[using deis]: ../using-deis/deploying-an-application.md
