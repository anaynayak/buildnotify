#!/bin/sh
# Build the sdist and wheel twice from the same commit and fail if the hashes differ.
set -eu

SOURCE_DATE_EPOCH=$(git log -1 --format=%ct)
export SOURCE_DATE_EPOCH
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

uv build --out-dir "$tmp/a" >/dev/null
uv build --out-dir "$tmp/b" >/dev/null

hash_dir() {
    (cd "$1" && for f in *; do
        if command -v sha256sum >/dev/null; then sha256sum "$f"; else shasum -a 256 "$f"; fi
    done)
}
hash_dir "$tmp/a" >"$tmp/a.sha256"
hash_dir "$tmp/b" >"$tmp/b.sha256"

if diff "$tmp/a.sha256" "$tmp/b.sha256"; then
    echo "Reproducible build:"
    cat "$tmp/a.sha256"
else
    echo "Two builds of the same commit differ" >&2
    exit 1
fi
