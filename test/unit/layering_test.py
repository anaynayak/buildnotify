import ast
from pathlib import Path

import pytest

import buildnotifylib.core

CORE = Path(buildnotifylib.core.__file__).parent
FORBIDDEN = ("buildnotifylib.adapters", "buildnotifylib.ui")


def imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules = [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    return modules + [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]


@pytest.mark.parametrize("path", sorted(CORE.glob("*.py")), ids=lambda path: path.name)
def test_core_should_not_import_adapters_or_ui(path):
    assert [module for module in imported_modules(path) if module.startswith(FORBIDDEN)] == []
