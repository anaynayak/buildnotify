import pytest

from buildnotifylib.build_icons import BuildIcons


@pytest.mark.functional
def test_should_consolidate_build_status(qtbot):
    aggregate_status = BuildIcons().for_aggregate_status('Success.Sleeping', "0")
    assert aggregate_status is not None


@pytest.mark.functional
def test_should_consolidate_build_status_with_failure_count(qtbot):
    aggregate_status = BuildIcons().for_aggregate_status('Success.Building', "1")
    assert aggregate_status is not None
