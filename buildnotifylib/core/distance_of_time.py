from datetime import datetime


class DistanceOfTime(object):
    def __init__(self, from_date):
        self.from_date = from_date

    def age(self):
        since_date = datetime.now(tz=self.from_date.tzinfo)

        distance_in_time = since_date - self.from_date
        distance_in_seconds = int(round(abs(distance_in_time.days * 86400 + distance_in_time.seconds)))
        distance_in_minutes = int(round(distance_in_seconds / 60))

        buckets = [(1, "1 minute"),
                   (45, "%s minutes" % distance_in_minutes),
                   (90, "1 hour"),
                   (1440, "%d hours" % (round(distance_in_minutes / 60.0))),
                   (2880, "1 day"),
                   (43220, "%d days" % (round(distance_in_minutes / 1440))),
                   (86400, "1 month"),
                   (525600, "%d months" % (round(distance_in_minutes / 43200))),
                   (1051200, "1 year")]
        default_bucket = "over %d years" % (round(distance_in_minutes / 525600))
        return next((desc for (time, desc) in buckets if distance_in_minutes <= time), default_bucket)
