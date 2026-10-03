"""Run each fuzz target on a few seed inputs so the targets don't rot."""

import importlib.util
from pathlib import Path

import pytest

FUZZ_DIR = Path(__file__).resolve().parent.parent / "fuzz"
CCTRAY = (
    b'<Projects><Project name="a" lastBuildStatus="Success" activity="Sleeping"'
    b' webUrl="http://x/" lastBuildTime="2024-01-01T00:00:00"/></Projects>'
)
SEEDS = {
    "fuzz_cctray": [CCTRAY, b"", b"<html/>", b"<Projects><Project/></Projects>", b"\xff\xfe<"],
    "fuzz_github": [b'{"workflow_runs": []}', b"", b"[]", b'{"workflow_runs": 1}', b"\xff"],
}


@pytest.mark.parametrize(("target", "seed"), [(t, s) for t, seeds in SEEDS.items() for s in seeds])
def test_target_handles_seed(target: str, seed: bytes) -> None:
    spec = importlib.util.spec_from_file_location(target, FUZZ_DIR / f"{target}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.test_one_input(seed)


def test_every_target_has_seeds() -> None:
    assert {p.stem for p in FUZZ_DIR.glob("fuzz_*.py")} == set(SEEDS)
