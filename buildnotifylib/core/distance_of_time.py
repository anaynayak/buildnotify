from datetime import datetime


class DistanceOfTime:
    def __init__(self, from_date: datetime, now: datetime | None = None):
        self.from_date = from_date
        self.now = now

    def _now(self) -> datetime:
        return self.now or datetime.now(tz=self.from_date.tzinfo)

    def relative(self) -> str:
        if self.from_date > self._now():
            return "in " + self.age()
        return self.age() + " ago"

    def age(self) -> str:
        distance_in_time = self._now() - self.from_date
        distance_in_seconds = int(round(abs(distance_in_time.days * 86400 + distance_in_time.seconds)))
        distance_in_minutes = int(round(distance_in_seconds / 60))

        buckets = [
            (1, "1 minute"),
            (45, f"{distance_in_minutes} minutes"),
            (90, "1 hour"),
            (1440, f"{round(distance_in_minutes / 60.0)} hours"),
            (2880, "1 day"),
            (43200, f"{round(distance_in_minutes / 1440)} days"),
            (86400, "1 month"),
            (525600, f"{round(distance_in_minutes / 43200)} months"),
            (1051200, "1 year"),
        ]
        default_bucket = f"over {round(distance_in_minutes / 525600)} years"
        return next((desc for (time, desc) in buckets if distance_in_minutes <= time), default_bucket)
