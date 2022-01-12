# rancher-fleet-slack-notifier

## Purpose
Ranchers Fleet is a really useful gitops tool for syncing a git repostiory with a running kubernetes cluster. Unfortunately, it does not include notifying in case clusters are not in sync. This tool was written to cover such a need. In this case, via a slack channel. It is meant to run in the same cluster where Rancher server is running. 

It will querry the fleet-default cluster list, and generate an alert if any clusters are not in ready state (meaning, either the cluster has an error, or is not in sync). When the cluster is returned to 'ready' state, another message is send indicating that as well. There is a 60 second sleep in between checks.

State of clusters is stored only in memory (sqlite). This means that every restart of this tool will resend any alerts, even if not new and sent already. The database could be moved to an external stateful DB if needed in the future.

## Deploy
First, a namespace is needed. (feel free to change namespace, but update other commands to match)
```
kubectl create namespace slack-notifier
```

Second, a secret needs to be created with the URLs and token. Simple way is from a file. For example:
a file called secrets.env with content:
```
SLACK_NOTIFY_URL=<from slack>
RANCHER_TOKEN=<bearer token for rancher user>
RANCHER_URL=http://rancher.cattle-system/v1/fleet.cattle.io.clusters/fleet-default
CHECK_INTERVAL=60
NOTIF_THRESHOLD=2
```
The RANCHER_URL, CHECK_INTERVAL and NOTIF_THRESHOLD can be omited and default values listed will be used.

- SLACK_NOTIFY_URL : webhook URL from slack
- RANCHER_TOKEN : Bearer token for authorization in rancher
- RANCHER_URL : Rancher API URL default='http://rancher.cattle-system/v1/fleet.cattle.io.clusters/fleet-default'
- CHECK_INTERVAL : Sleep period (in seconds) between checks default=60
- NOTIF_THRESHOLD : How many times a cluster must out of sync before triggering alert default=2


If using a secrets.env with above values, it could be inserted with the following command
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
