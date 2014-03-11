
from datetime import datetime
import pytz

class DistanceOfTime:
    def __init__(self, from_date, timezone):
        self.from_date = from_date
        self.timezone = timezone
        
    def age(self):
        since_date = datetime.now(tz=pytz.timezone(self.timezone)).replace(tzinfo=None)

        distance_in_time = since_date - self.from_date
        distance_in_seconds = int(round(abs(distance_in_time.days * 86400 + distance_in_time.seconds)))
        distance_in_minutes = int(round(distance_in_seconds/60))

        if distance_in_minutes <= 1:
            return "1 minute"
        elif distance_in_minutes < 45:
            return "%s minutes" % distance_in_minutes
        elif distance_in_minutes < 90:
            return "1 hour"
        elif distance_in_minutes < 1440:
            return "%d hours" % (round(distance_in_minutes / 60.0))
        elif distance_in_minutes < 2880:
            return "1 day"
        elif distance_in_minutes < 43220:
            return "%d days" % (round(distance_in_minutes / 1440))
        elif distance_in_minutes < 86400:
            return "1 month"
        elif distance_in_minutes < 525600:
            return "%d months" % (round(distance_in_minutes / 43200))
        elif distance_in_minutes < 1051200:
            return "1 year"
        else:
            return "over %d years" % (round(distance_in_minutes / 525600))
