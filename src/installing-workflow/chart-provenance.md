# Chart Provenance

As of Workflow [v2.8.0](../changelogs/v2.8.0.md), Deis has released [Kubernetes Helm][helm] charts for Workflow
and for each of its [components](../understanding-workflow/components.md).

Helm provides tools for establishing and verifying chart integrity.  (For an overview, see the [Provenance](https://github.com/kubernetes/helm/blob/master/docs/provenance.md) doc.)  All release charts from the Deis Workflow team are now signed using this mechanism.

The full `Deis, Inc. (Helm chart signing key) <security@deis.com>` public key can be found [here](../security/1d6a97d0.txt), as well as the [pgp.mit.edu](http://pgp.mit.edu/pks/lookup?op=vindex&fingerprint=on&search=0x17E526B51D6A97D0) keyserver and the official Deis Keybase [account][deis-keybase].  The key's fingerprint can be cross-checked against all of these sources.

## Verifying a signed chart

The public key mentioned above must exist in a local keyring before a signed chart can be verified.

To add it to the default `~/.gnupg/pubring.gpg` keyring, any of the following commands will work:

```
$ # via our hosted location
$ curl https://deis.com/workflow/docs/security/1d6a97d0.txt | gpg --import

$ # via the pgp.mit.edu keyserver
$ gpg --keyserver pgp.mit.edu --recv-keys 1D6A97D0

$ # via Keybase with account...
$ keybase follow deis
$ keybase pgp pull

$ # via Keybase by curl
$ curl https://keybase.io/deis/key.asc | gpg --import
```

Charts signed with this key can then be verified when fetched:

```
$ helm repo add deis https://charts.deis.com/workflow
"deis" has been added to your repositories

$ helm fetch --verify deis/workflow
Verification: &{0xc420725db0 sha256:6599eb45055766cac92a1f6f1dea96ca3bf49a2c388aed02896806f6fd39cc7b workflow-v2.10.0.tgz}
```

One can then inspect the fetched `workflow-v2.10.0.tgz.prov` provenance file.

If the chart was not signed, the command above would result in:

```
Error: Failed to fetch provenance "https://charts.deis.com/workflow/workflow-v2.10.0.tgz.prov"
```

Alternatively, the chart can also be verified at install time:

```
$ helm install --verify deis/workflow --namespace deis
Fetched deis/workflow to workflow-v2.10.0.tgz
NAME: olfactory-star
LAST DEPLOYED: Thu Jan 05 11:45:44 2017
NAMESPACE: deis
STATUS: DEPLOYED
...
```

Having done so, one is assured of the origin and authenticity of any installed Workflow chart released by Deis.

[helm]: https://github.com/kubernetes/helm/blob/master/docs/install.md
[deis-keybase]: https://keybase.io/deis
