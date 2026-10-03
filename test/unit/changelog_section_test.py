import pytest

from scripts.changelog_section import extract, main

CHANGELOG = """## [Unreleased]

## [3.0.0] - 2026-10-02

### Added
- Thing

## [2.1.0] - 2020-01-01

### Fixed
- Old thing
"""


def test_should_return_only_the_requested_section():
    assert extract(CHANGELOG, "3.0.0") == "### Added\n- Thing"


def test_should_return_the_last_section_to_the_end_of_the_file():
    assert extract(CHANGELOG, "2.1.0") == "### Fixed\n- Old thing"


def test_should_not_match_a_version_that_is_a_prefix_of_another():
    with pytest.raises(ValueError):
        extract(CHANGELOG, "3.0")


def test_should_reject_an_unknown_version():
    with pytest.raises(ValueError, match="9.9.9"):
        extract(CHANGELOG, "9.9.9")


def test_should_accept_a_tag_name_and_print_the_notes(tmp_path, capsys):
    path = tmp_path / "CHANGELOG"
    path.write_text(CHANGELOG)
    assert main(["changelog_section.py", "v3.0.0", str(path)]) == 0
    assert capsys.readouterr().out == "### Added\n- Thing\n"


def test_should_fail_on_an_empty_section(tmp_path):
    path = tmp_path / "CHANGELOG"
    path.write_text(CHANGELOG)
    assert main(["changelog_section.py", "Unreleased", str(path)]) == 1
