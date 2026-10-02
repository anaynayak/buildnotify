from datetime import datetime


def relative(then: datetime, now: datetime) -> str:
    if then > now:
        return "in " + age(then, now)
    return age(then, now) + " ago"


def age(then: datetime, now: datetime) -> str:
    distance = now - then
    minutes = int(round(abs(distance.days * 86400 + distance.seconds) / 60))
    buckets = [
        (1, "1 minute"),
        (45, f"{minutes} minutes"),
        (90, "1 hour"),
        (1440, f"{round(minutes / 60.0)} hours"),
        (2880, "1 day"),
        (43200, f"{round(minutes / 1440)} days"),
        (86400, "1 month"),
        (525600, f"{round(minutes / 43200)} months"),
        (1051200, "1 year"),
    ]
    return next((text for limit, text in buckets if minutes <= limit), f"over {round(minutes / 525600)} years")
