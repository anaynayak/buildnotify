from datetime import datetime
from pytz import timezone

from buildnotifylib.core.distance_of_time import DistanceOfTime


def test_should_get_relative_distance():
    assert "1 minute" == DistanceOfTime(datetime.now(timezone('US/Eastern'))).age()


def test_should_get_relative_distance_for_tz_unaware():
    assert "1 minute" == DistanceOfTime(datetime.now()).age()
