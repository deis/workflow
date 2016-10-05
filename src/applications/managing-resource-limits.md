## Managing Application Resource Limits

Deis Workflow supports restricting memory and CPU shares of each process. Limits set on a per-process type are given to
Kubernetes as both a request and limit. Which means you guarantee 'X' amount of resource for a process as well as limit
the process from using more than 'X'.

## Limiting Memory

If you set a limit that is out of range for your cluster, Kubernetes will be unable to schedule your application
processes into the cluster!

Available units for memory are:

| Unit | Amount           |
| ---  | ---              |
| B    | Bytes            |
| K    | KiB (Power of 2) |
| M    | MiB (Power of 2) |
| G    | GiB (Power of 2) |

!!! important
    The minimum memory limit allowed is 4MiB.

Use `deis limits:set` to restrict memory by process type:

```
$ deis limits:set web=64M
Applying limits... done

=== indoor-whitecap Limits

--- Memory
web     64M

--- CPU
Unlimited
```

If you would like to remove any configured memory limits use `deis limits:unset web`:

```
$ deis limits:unset web
Applying limits... done

=== indoor-whitecap Limits

--- Memory
Unlimited

--- CPU
Unlimited
```

## Limiting CPU

You can also use `deis limits:set --cpu` to restrict CPU shares. CPU shares are tracked in milli-cores. One CPU core is
equivalent to 1000 milli-cores. To dedicate half a core to your process, you would need 500 milli-cores or 500m.

| Unit  | Amount                            |
| ---   | ---                               |
| 1000m | 1000 milli-cores == 100% CPU core |
| 500m  | 500 milli-cores == 50% CPU core   |
| 250m  | 250 milli-cores == 25% CPU core   |
| 100m  | 100 milli-cores == 10% CPU core   |

```
$ deis limits:set web=250m --cpu
Applying limits... done

=== indoor-whitecap Limits

--- Memory
web     64M

--- CPU
web     250m
```

You can verify the CPU and memory limits by inspecting the application process Pod with `kubectl`:

```
$ deis ps
=== indoor-whitecap Processes
--- web:
indoor-whitecap-v14-web-8slcj up (v14)
$ kubectl --namespace=indoor-whitecap describe po indoor-whitecap-v14-web-8slcj
Name:       indoor-whitecap-v14-web-8slcj
Containers:
    QoS Tier:
      cpu:  Guaranteed
      memory:   Guaranteed
    Limits:
      cpu:  250m
      memory:   64Mi
    Requests:
      memory:       64Mi
      cpu:      250m
```

!!! important
    If you restrict resources to the point where containers do not start,
    the `limits:set` command will hang.  If this happens, use CTRL-C
    to break out of `limits:set` and use `limits:unset` to revert.

To unset a CPU limit use `deis limits:unset web --cpu`:

```
$ deis limits:unset web --cpu
Applying limits... done

=== indoor-whitecap Limits

--- Memory
Unlimited

--- CPU
Unlimited
```
