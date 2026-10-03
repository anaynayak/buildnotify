# Woodpecker CI

Woodpecker publishes a cctray feed for each repository through its badge API.

## URL pattern

`https://<host>/api/badges/<owner>/<repo>/cc.xml`, as listed on [cctray.org](https://cctray.org/servers/).

On [Crow CI](crow.md), a Woodpecker fork, this path returns HTML. Use the Crow path there.

## Sign in

Choose `None` for a public repository. For a private one choose `Token`.

## Example

```text
https://ci.example.org/api/badges/octo-org/hello-world/cc.xml
```
