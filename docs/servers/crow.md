---
description: Watch Crow CI repositories in BuildNotify through the per-repository cctray feed.
---

# Crow CI

Crow CI publishes a cctray feed for each repository.

## URL pattern

`https://<host>/api/v1/badges/<owner>/<repo>/cc.xml`

This was checked against a live Crow server. The Woodpecker path `/api/badges/...` returns HTML on Crow, so a feed URL copied from a Woodpecker guide fails.

## Sign in

Choose `None`. The feed is readable without authentication, so anyone who knows the URL can read it.

## Example

```text
https://crow.example.org/api/v1/badges/octo-org/hello-world/cc.xml
```

## Caveats

1. The feed reports the newest pipeline of any branch, not one branch. A failing feature branch turns the project red.
2. While a pipeline runs, its status is `Unknown`.
3. The feed needs no authentication, as noted above.
