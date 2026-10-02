import ast
import subprocess
import sys
from pathlib import Path

import pytest

import buildnotifylib.core

CORE = Path(buildnotifylib.core.__file__).parent
CORE_MODULES = sorted(CORE.glob("*.py"))
FORBIDDEN = ("buildnotifylib.adapters", "buildnotifylib.ui", "PyQt5", "PySide6", "requests", "keyring")


def imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules = [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    return modules + [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]


def forbidden(module: str) -> bool:
    return any(module == prefix or module.startswith(prefix + ".") for prefix in FORBIDDEN)


@pytest.mark.parametrize("path", CORE_MODULES, ids=lambda path: path.name)
def test_core_should_not_import_qt_adapters_or_ui(path):
    assert [module for module in imported_modules(path) if forbidden(module)] == []


def test_importing_all_of_core_should_load_no_qt_requests_or_keyring():
    imports = "; ".join(f"import buildnotifylib.core.{path.stem}" for path in CORE_MODULES)
    code = f"import sys; {imports}; print(sorted(m for m in sys.modules if m.split('.')[0] in {FORBIDDEN[2:]!r}))"
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True)
    assert result.stdout.strip() == "[]"
