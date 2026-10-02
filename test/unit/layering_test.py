import ast
import subprocess
import sys
from pathlib import Path

import pytest

import buildnotifylib
import buildnotifylib.adapters
import buildnotifylib.core
import buildnotifylib.ui

CORE = Path(buildnotifylib.core.__file__).parent
CORE_MODULES = sorted(CORE.glob("*.py"))
ADAPTER_MODULES = sorted(Path(buildnotifylib.adapters.__file__).parent.glob("*.py"))
PACKAGE = Path(buildnotifylib.__file__).parent
UI = Path(buildnotifylib.ui.__file__).parent
UI_MODULES = sorted(UI.rglob("*.py"))
NON_UI_MODULES = sorted(
    path for path in PACKAGE.rglob("*.py") if not path.is_relative_to(UI) and path.name != "__main__.py"
)
FORBIDDEN = ("buildnotifylib.adapters", "buildnotifylib.ui", "PyQt5", "PySide6", "requests", "keyring")
CORE_MAY_IMPORT = ("buildnotifylib.core",)
ADAPTERS_MAY_IMPORT = ("buildnotifylib.core", "buildnotifylib.adapters", "buildnotifylib.version")
UI_MAY_IMPORT = ADAPTERS_MAY_IMPORT + ("buildnotifylib.ui",)


def imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules = [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    return modules + [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]


def within(module: str, prefixes: tuple[str, ...]) -> bool:
    return any(module == prefix or module.startswith(prefix + ".") for prefix in prefixes)


def outside_layer(path: Path, allowed: tuple[str, ...]) -> list[str]:
    internal = [module for module in imported_modules(path) if within(module, ("buildnotifylib",))]
    return [module for module in internal if not within(module, allowed)]


@pytest.mark.parametrize("path", CORE_MODULES, ids=lambda path: path.name)
def test_core_should_not_import_qt_adapters_or_ui(path):
    assert [module for module in imported_modules(path) if within(module, FORBIDDEN)] == []


@pytest.mark.parametrize("path", CORE_MODULES, ids=lambda path: path.name)
def test_core_should_import_only_core_from_buildnotifylib(path):
    assert outside_layer(path, CORE_MAY_IMPORT) == []


@pytest.mark.parametrize("path", ADAPTER_MODULES, ids=lambda path: path.name)
def test_adapters_should_not_import_ui(path):
    assert outside_layer(path, ADAPTERS_MAY_IMPORT) == []


@pytest.mark.parametrize("path", UI_MODULES, ids=lambda path: str(path.relative_to(UI)))
def test_ui_should_import_only_core_adapters_and_ui(path):
    assert outside_layer(path, UI_MAY_IMPORT) == []


@pytest.mark.parametrize("path", NON_UI_MODULES, ids=lambda path: str(path.relative_to(PACKAGE)))
def test_only_the_entry_point_should_import_the_ui(path):
    assert [module for module in imported_modules(path) if within(module, ("buildnotifylib.ui",))] == []


def test_should_flag_an_adapter_importing_the_ui(tmp_path):
    module = tmp_path / "bad.py"
    module.write_text("from buildnotifylib.ui.app_menu import AppMenu\nimport buildnotifylib.ui.poller\n")
    assert outside_layer(module, ADAPTERS_MAY_IMPORT) == ["buildnotifylib.ui.poller", "buildnotifylib.ui.app_menu"]


def test_importing_all_of_core_should_load_no_qt_requests_or_keyring():
    imports = "; ".join(f"import buildnotifylib.core.{path.stem}" for path in CORE_MODULES)
    code = f"import sys; {imports}; print(sorted(m for m in sys.modules if m.split('.')[0] in {FORBIDDEN[2:]!r}))"
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert result.stdout.strip() == "[]"
