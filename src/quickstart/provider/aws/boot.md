export KUBE_AWS_ZONE=us-west-2a
export KUBERNETES_PROVIDER=aws
export KUBE_ENABLE_INSECURE_REGISTRY=true
export MASTER_SIZE=t2.medium
export NODE_SIZE=t2.large
export NUM_NODES=2
export MINION_ROOT_DISK_SIZE=100

kube-up.sh

exit criteria, kubectl should be working and pointed at the cluster

[next install workflow](install-aws.md)
