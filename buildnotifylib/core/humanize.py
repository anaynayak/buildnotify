from datetime import datetime

UNITS = [(525600, "y"), (1440, "d"), (60, "h"), (1, "m")]


def compact(then: datetime, now: datetime) -> str:
    """A short age for a menu row, such as "18m", "11h" or "3d", or "in 5h" for a time ahead of now."""
    minutes = round(abs((now - then).total_seconds()) / 60)
    if minutes == 0:
        return "now"
    size, unit = next((size, unit) for size, unit in UNITS if minutes >= size)
    text = f"{minutes // size}{unit}"
    return f"in {text}" if then > now else text
