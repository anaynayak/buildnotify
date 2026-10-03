---
description: Watch Jenkins builds in BuildNotify through the CCTray XML plugin feed, with the URL pattern and sign-in options.
---

# Jenkins

Jenkins publishes a cctray feed through the CCTray XML plugin.

## URL pattern

1. `https://<host>/cc.xml` lists every job. This path is on [cctray.org](https://cctray.org/servers/).
2. `https://<host>/view/<name>/cc.xml` limits the feed to one view. The [CCtray XML plugin](https://plugins.jenkins.io/cctray-xml/) provides `cc.xml` for Jenkins views, so the same path under `/view/<name>/` serves one view.

## Sign in

Choose `None` for a Jenkins that allows anonymous reads. Otherwise choose `Username and password`, or `Token` for a Bearer token. The credentials are kept in the system keyring.

## Example

```text
https://jenkins.example.org/view/platform/cc.xml
```

Paste the URL into the server dialog, run Test connection, and untick the jobs you don't want.
