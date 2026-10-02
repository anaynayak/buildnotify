from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from buildnotifylib.core.distance_of_time import DistanceOfTime


def test_should_get_relative_distance():
    assert "1 minute" == DistanceOfTime(datetime.now(ZoneInfo('US/Eastern'))).age()


def test_should_get_relative_distance_for_tz_unaware():
    assert "1 minute" == DistanceOfTime(datetime.now()).age()


NOW = datetime(2026, 1, 1, 12, 0, 0)


def _age(minutes):
    return DistanceOfTime(NOW - timedelta(minutes=minutes), now=NOW).age()


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
