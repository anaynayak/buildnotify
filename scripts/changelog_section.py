"""Print one version's section of the CHANGELOG, for use as GitHub Release notes."""

import re
import sys
from pathlib import Path


def extract(changelog: str, version: str) -> str:
    """Return the body under `## [version]`, up to the next `## [` heading, stripped."""
    start = re.search(rf"^## \[{re.escape(version)}\].*$", changelog, re.MULTILINE)
    if start is None:
        raise ValueError(f"No section for version {version} in the CHANGELOG")
    rest = changelog[start.end() :]
    end = re.search(r"^## \[", rest, re.MULTILINE)
    body = rest[: end.start()] if end else rest
    return body.strip()


def main(argv: list[str]) -> int:
    version, path = argv[1], Path(argv[2] if len(argv) > 2 else "CHANGELOG")
    try:
        notes = extract(path.read_text(encoding="utf-8"), version.removeprefix("v"))
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    if not notes:
        print(f"The CHANGELOG section for {version} is empty", file=sys.stderr)
        return 1
    print(notes)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
