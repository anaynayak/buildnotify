export QT_QPA_PLATFORM := "offscreen"

# List the recipes
default:
    @just --list

# Run the test suite
test *args:
    uv run --locked pytest -q {{args}}

# Lint and check formatting
lint:
    uv run --locked ruff check
    uv run --locked ruff format --check

# Apply ruff fixes and formatting
fmt:
    uv run --locked ruff check --fix
    uv run --locked ruff format

# Type-check with mypy
types:
    uv run --locked mypy

# Regenerate the hashed requirements for the fuzz build, pinned to uv.lock versions
fuzz-reqs:
    uv export --no-dev --no-emit-project --no-hashes --no-header --no-annotate | uv pip compile .clusterfuzzlite/requirements.in -c /dev/stdin --generate-hashes --no-header --no-annotate -o .clusterfuzzlite/requirements.txt -q

# Build the sdist and wheel into dist/
build:
    uv build

# Run the app against local fixture feeds with throwaway settings and no keychain
demo *args:
    uv run --locked python scripts/demo.py {{args}}

# Render the docs screenshots offscreen into docs/images
screenshots:
    uv run --locked python scripts/screenshots.py

# Build twice and fail if the sdist or wheel hashes differ
repro:
    scripts/repro-check.sh

# Write a CycloneDX SBOM of the runtime dependencies from uv.lock to sbom.cdx.json
sbom:
    uv export --locked --no-dev --no-emit-project --format cyclonedx1.5 -o sbom.cdx.json
