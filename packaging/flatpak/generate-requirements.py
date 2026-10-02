"""Write python3-requirements.json, the flatpak-builder module with BuildNotify's Python deps.

Runtime deps are pinned by uv.lock, for Linux on the runtime's Python 3.13. PySide6 is left out
because io.qt.PySide.BaseApp provides it. Pure-Python packages use their py3-none-any wheel and
compiled ones a manylinux wheel per Flathub arch. hatchling, which builds the app, is pinned here.
Run after uv.lock changes: uv run --with packaging python packaging/flatpak/generate-requirements.py
"""

import json
import subprocess
import tomllib
import urllib.request
from pathlib import Path

from packaging.markers import Marker

HERE = Path(__file__).parent
ROOT = HERE.parent.parent
PYTHON = "3.13"
PROVIDED = {"pyside6", "pyside6-addons", "pyside6-essentials", "shiboken6"}
BUILD = {"hatchling": "1.32.4", "pathspec": "1.1.1", "pluggy": "1.6.0", "tomlkit": "0.15.1"}
BUILD |= {"trove-classifiers": "2026.9.21.13"}
ARCHES = ("x86_64", "aarch64")
COMPILED_TAGS = ("cp313-cp313-manylinux", "abi3-manylinux_2_34")
PIP = 'pip3 install --exists-action=i --no-index --find-links="file://${PWD}" --prefix=${FLATPAK_DEST}'
PIP += " --no-build-isolation"


def runtime_pins() -> dict[str, str]:
    exported = subprocess.run(
        ["uv", "export", "--frozen", "--no-dev", "--no-hashes", "--no-emit-project", "--no-header", "--no-annotate"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    env = {"python_version": PYTHON, "python_full_version": f"{PYTHON}.0"}
    env |= {"sys_platform": "linux", "platform_system": "Linux"}
    pins = {}
    for line in exported.splitlines():
        requirement, _, marker = line.partition(" ; ")
        name, _, version = requirement.partition("==")
        if name not in PROVIDED and applies(marker, env):
            pins[name] = version
    return pins


def applies(marker: str, env: dict[str, str]) -> bool:
    return not marker or Marker(marker).evaluate(env)


def locked_wheels() -> dict[str, list[dict]]:
    lock = tomllib.loads((ROOT / "uv.lock").read_text())
    wheels = {}
    for package in lock["package"]:
        found = package.get("wheels", [])
        wheels[package["name"]] = [{"url": w["url"], "sha256": w["hash"].removeprefix("sha256:")} for w in found]
    return wheels


def pypi_wheels(name: str, version: str) -> list[dict]:
    with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/{version}/json") as response:
        files = json.load(response)["urls"]
    return [{"url": f["url"], "sha256": f["digests"]["sha256"]} for f in files if f["packagetype"] == "bdist_wheel"]


def sources(wheels: list[dict]) -> list[dict]:
    pure = [w for w in wheels if w["url"].endswith("-none-any.whl")]
    if pure:
        return [{"type": "file", **pure[0]}]
    return [{"type": "file", **pick(wheels, arch), "only-arches": [arch]} for arch in ARCHES]


def pick(wheels: list[dict], arch: str) -> dict:
    return next(w for tag in COMPILED_TAGS for w in wheels if tag in w["url"] and w["url"].endswith(f"{arch}.whl"))


def module(name: str, pins: dict[str, str], wheels: dict[str, list[dict]], cleanup: list[str]) -> dict:
    requirements = " ".join(f'"{n}=={v}"' for n, v in pins.items())
    return {
        "name": name,
        "buildsystem": "simple",
        "build-commands": [f"{PIP} {requirements}"],
        "sources": [s for n in pins for s in sources(wheels[n])],
        "cleanup": cleanup,
    }


def main() -> None:
    locked = locked_wheels()
    build = {n: pypi_wheels(n, v) for n, v in BUILD.items()}
    modules = [module("python3-runtime", runtime_pins(), locked, []), module("python3-hatchling", BUILD, build, ["*"])]
    parent = {"name": "python3-requirements", "buildsystem": "simple", "build-commands": [], "modules": modules}
    (HERE / "python3-requirements.json").write_text(json.dumps(parent, indent=4) + "\n")


if __name__ == "__main__":
    main()
