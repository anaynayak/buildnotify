---
description: Use BuildNotify with any server that publishes a cctray.xml feed, such as Concourse and Drone CI.
---

# Other cctray servers

Any server that publishes a cctray.xml feed works. [cctray.org/servers](https://cctray.org/servers/) lists the servers and their feed paths. Two are listed here.

## URL patterns

1. Concourse: `https://<host>/api/v1/teams/<team>/cc.xml`
2. Drone CI: `https://<host>/api/badges/<owner>/<name>/cc.xml`

Both come from [cctray.org](https://cctray.org/servers/) and haven't been checked against a live server.

## Sign in

Choose `None`, `Username and password` or `Token` (a Bearer token, without the `Bearer` keyword). Use whatever the server needs to read the feed.

## Example

```text
https://concourse.example.org/api/v1/teams/main/cc.xml
```

The URL must start with `http://` or `https://`. A URL typed without one gets `https://`.
