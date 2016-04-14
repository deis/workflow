# Releasing a New Deis Version

This document describes how to release a new Deis version. It's targetted toward the Deis core
maintainers.

# Manual Testing

After the chart is created with the immutable Docker image tags that represent the final images
(i.e. the ones that will be re-tagged to the immutable release tag, such as `2.0.0-beta2`), it
should be manually tested by as many people as possible. Special attention should be paid to the
user experience, both from an operator and developer perspective.

Our goal is to test with as many object storage and Kubernetes installation configurations as
possible, to ensure there are no gaps in configuration or functionality. See below for a testing
matrix.

Object Storage / Kubernetes Install | Kube-Solo | Google Container Engine | AWS | Micro-Kube | Vagrant |
----------------------------------- | --------- | ----------------------- | --- | ---------- | ------- |
Default (Minio)                     |
Google Cloud Storage                |
Amazon S3                           |
