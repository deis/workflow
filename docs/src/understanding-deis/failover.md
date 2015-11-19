# Failover

## Three Node Cluster

### Losing One of Three Nodes

Losing one of three nodes will have the following effects:

- Ceph will enter a health warn state but will continue to function.
- Anything scheduled on the downed node will be rescheduled to the other two nodes.
  If your remaining nodes don't have the resources to run the new units, this could
  take down the entire platform
- When you scale up to three nodes again, Ceph and Etcd will still think one member is down.
  You will need to manually remove the downed node from Ceph and Etcd.

### Losing Two of Three Nodes

Losing two of three nodes will have the following effects:

- Ceph will enter a degraded state and go into read-only mode.
- Etcd will enter a degraded state and go into read-only mode.
- Anything scheduled on the downed node will be rescheduled to remaining node.
  If your remaining node doesn't have the resources to run the new units, this could
  take down the entire platform.
- When you scale up to three nodes again, Ceph and Etcd will still think two members are down.
  You will need to manually remove the downed nodes from Ceph and Etcd.

## Larger Clusters

If you have more than three nodes, Deis can tolerate node failure without issue.
Here are a few things to keep in mind:

- You have to manually remove downed nodes from Etcd and Ceph. Ceph and Etcd think downed nodes
  might still be functioning but out of communication with the main cluster. If you don't remove
  downed nodes, they could eventually outnumber running nodes. This will cause Ceph and etcd to go
  into read only mode to prevent a split brained cluster.
- Ceph on Deis stores three replicas of all data. If a node goes down, Ceph doesn't replicate the data on
  that node because it expects the node will come back. Manually removing the node will resolve this.
- If the database is rescheduled, it has to go through a recovery process wherever it is rescheduled, causing
  controller downtime (generally less than a minute).
- User apps should be scaled to reside on multiple hosts. That way, if one node goes down your app will continue to
  function without downtime.
