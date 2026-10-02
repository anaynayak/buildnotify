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

# Build the sdist and wheel into dist/
build:
    uv build

# Regenerate the Qt UI modules and icon resources
ui:
    uv run --locked pyuic5 --from-imports -o buildnotifylib/generated/preferences_ui.py data/preferences.ui
    uv run --locked pyuic5 --from-imports -o buildnotifylib/generated/server_configuration_ui.py data/server_configuration.ui
    uv run --locked pyrcc5 icons/icons.qrc -o buildnotifylib/generated/icons_rc.py
