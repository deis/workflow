# Deis Integration Tests

This directory contains [Ginkgo](http://onsi.github.io/ginkgo)/[Gomega](http://onsi.github.io/gomega) based integration tests, which exercise
the Deis CLI to extensively test the platform.

# Resetting Cluster State

Periodically, tests may not clean up after themselves. While this is an ongoing issue,
for which we're working on a permanent fix (possible in [this GH issue](https://github.com/deis/workflow/issues/125))),
below are commands you can run to work around the failure:

```console
$ kubectl exec -it deis-workflow-qoxhz python manage.py shell
Python 2.7.10 (default, Aug 13 2015, 12:27:27)
[GCC 4.9.2] on linux2
>>> from django.contrib.auth import get_user_model
>>> m = get_user_model()
>>> m.objects.exclude(username='AnonymousUser').delete()
>>> m.objects.all()                                     
```
