# rancher-fleet-slack-notifier

## Purpose
Ranchers Fleet is a really useful gitops tool for syncing a git repostiory with a running kubernetes cluster. Unfortunately, it does not include notifying in case clusters are not in sync. This tool was written to cover such a need. In this case, via a slack channel. It is meant to run in the same cluster where Rancher server is running. 

It will querry the fleet-default cluster list, and generate an alert if any clusters are not in ready state (meaning, either the cluster has an error, or is not in sync). When the cluster is returned to 'ready' state, another message is send indicating that as well. There is a 60 second sleep in between checks.

State of clusters is stored only in memory (sqlite). This means that every restart of this tool will resend any alerts, even if not new and sent already. The database could be moved to an external stateful DB if needed in the future.

<!-- ## Build container image
If not using container image provided here, an image needs to be built and pushed to an appropriate repository, following is only an exameple.

```
nerdctl build -t punasusi/slack-notifier:0.0.5 . 
nerdctl push punasusi/slack-notifier:0.0.5
```

> nerdctl is part of rancherdesktop and replaces docker command for most everything -->

## Deploy
First, a namespace is needed. (feel free to change namespace, but update other commands to match)
```
kubectl create namespace slack-notifier
```

Second, a secret needs to be created with the URLs and token. Simple way is from a file. For example:
a file called secrets.env with content:
```
SLACK_NOTIFY_URL=<from slack>
RANCHER_URL=http://rancher.cattle-system/v1/fleet.cattle.io.clusters/fleet-default
RANCHER_TOKEN=<bearer token for rancher user>
```
could be used, and inserted with the following command
```
kubectl --namespace slack-notifier create secret generic slack-creds --from-env-file secrets.env        
```

Then, apply the kubernetes deployment yaml found in the kubernetes directory
```
kubectl --namespace slack-notifier create -f kubernetes/deployment.yaml
```


## TODO
- [ ] make notification text configurable
- [ ] better logging