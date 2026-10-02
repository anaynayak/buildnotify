from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from hypothesis import given
from hypothesis import strategies as st

from buildnotifylib.core.humanize import age, relative

NOW = datetime(2026, 1, 1, 12, 0, 0)


def _age(minutes):
    return age(NOW - timedelta(minutes=minutes), NOW)


def test_should_get_relative_distance_for_tz_aware():
    now = datetime(2026, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("US/Eastern"))
    assert age(now - timedelta(seconds=20), now) == "1 minute"


def test_should_get_relative_distance_for_tz_unaware():
    assert age(NOW - timedelta(seconds=20), NOW) == "1 minute"


def test_should_describe_each_bucket():
    assert _age(0) == "1 minute"
    assert _age(30) == "30 minutes"
    assert _age(60) == "1 hour"
    assert _age(300) == "5 hours"
    assert _age(2000) == "1 day"
    assert _age(10 * 1440) == "10 days"
    assert _age(60 * 1440) == "1 month"
    assert _age(180 * 1440) == "6 months"
    assert _age(400 * 1440) == "1 year"
    assert _age(3 * 525600) == "over 3 years"


def test_should_switch_to_months_after_30_days():
    assert _age(43210) == "1 month"


def test_should_describe_past_times_as_ago():
    assert relative(NOW - timedelta(hours=5), NOW) == "5 hours ago"


def test_should_describe_future_times_as_in():
    assert relative(NOW + timedelta(hours=5), NOW) == "in 5 hours"


@given(st.timedeltas(min_value=timedelta(0), max_value=timedelta(days=36500)))
def test_age_should_not_depend_on_direction(offset):
    assert age(NOW - offset, NOW) == age(NOW + offset, NOW)
