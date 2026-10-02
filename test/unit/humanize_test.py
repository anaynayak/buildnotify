from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from hypothesis import given
from hypothesis import strategies as st

from buildnotifylib.core.humanize import compact

NOW = datetime(2026, 1, 1, 12, 0, 0)


def compact_age(minutes):
    return compact(NOW - timedelta(minutes=minutes), NOW)


def test_should_get_a_compact_age_for_tz_aware():
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("US/Eastern"))
    assert compact(now - timedelta(minutes=18, seconds=20), now) == "18m"


def test_should_describe_each_compact_bucket():
    assert compact_age(0) == "now"
    assert compact_age(1) == "1m"
    assert compact_age(18) == "18m"
    assert compact_age(59) == "59m"
    assert compact_age(60) == "1h"
    assert compact_age(11 * 60 + 40) == "11h"
    assert compact_age(1440) == "1d"
    assert compact_age(3 * 1440 + 600) == "3d"
    assert compact_age(364 * 1440) == "364d"
    assert compact_age(400 * 1440) == "1y"


def test_should_mark_compact_future_times_with_in():
    assert compact(NOW + timedelta(hours=5), NOW) == "in 5h"


@given(st.timedeltas(min_value=timedelta(minutes=1), max_value=timedelta(days=36500)))
def test_compact_should_not_depend_on_direction_beyond_the_in(offset):
    assert "in " + compact(NOW - offset, NOW) == compact(NOW + offset, NOW)
