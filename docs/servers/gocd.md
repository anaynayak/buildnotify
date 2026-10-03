---
description: Watch GoCD pipelines in BuildNotify through the built-in cctray feed, with the URL pattern and sign-in options.
---

# GoCD

GoCD serves a cctray feed from its own server. No plugin is needed.

## URL pattern

`https://<host>/go/cctray.xml`, as listed on [cctray.org](https://cctray.org/servers/).

## Sign in

Choose `None` if the server allows anonymous reads. Otherwise choose `Username and password`. The credentials are kept in the system keyring.

## Example

```text
https://gocd.example.org/go/cctray.xml
```
