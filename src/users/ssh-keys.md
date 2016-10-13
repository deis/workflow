# Users and SSH Keys

For **Dockerfile** and **Buildpack** based application deploys via `git push`, Deis Workflow identifies users via SSH
keys. SSH keys are pushed to the platform and must be unique to each user. Users may have multiple SSH keys as needed.

## Generate an SSH Key

If you do not already have an SSH key or would like to create a new key for Deis Workflow, generate a new key using
`ssh-keygen`:

```
$ ssh-keygen -f ~/.ssh/id_deis -t rsa
Generating public/private rsa key pair.
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /Users/admin/.ssh/id_deis.
Your public key has been saved in /Users/admin/.ssh/id_deis.pub.
The key fingerprint is:
3d:ac:1f:f4:83:f7:64:51:c1:7e:7f:80:b6:70:36:c9 admin@plinth-23437.local
The key's randomart image is:
+--[ RSA 2048]----+
|              .. |
|               ..|
|           . o. .|
|         o. E .o.|
|        S == o..o|
|         o +.  .o|
|        . o + o .|
|         . o =   |
|          .   .  |
+-----------------+
$ ssh-add ~/.ssh/id_deis
Identity added: /Users/admin/.ssh/id_deis (/Users/admin/.ssh/id_deis)
```

## Adding and Removing SSH Keys

By publishing the **public** half of your SSH key to Deis Workflow the component responsible for receiving `git push`
will be able to authenticate the user and ensure that they have access to the destination application.

```
$ deis keys:add ~/.ssh/id_deis.pub
Uploading id_deis.pub to deis... done
```

You can always view the keys associated with your user as well:

```
$ deis keys:list
=== admin Keys
admin@plinth-23437.local ssh-rsa AAAAB3Nz...3437.local
admin@subgenius.local ssh-rsa AAAAB3Nz...nius.local
```

Remove keys by their name:
```
$ deis keys:remove admin@plinth-23437.local
Removing admin@plinth-23437.local SSH Key... don
```
