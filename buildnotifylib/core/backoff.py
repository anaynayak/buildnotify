from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

FIBONACCI = (1, 2, 3, 5, 8, 13, 21)


@dataclass(frozen=True)
class Backoff:
    """Consecutive failed polls per server url; a failure is shown when its count is a Fibonacci number."""

    failures: Mapping[str, int] = field(default_factory=dict)

    def advance(self, urls: Sequence[str]) -> tuple["Backoff", list[str]]:
        failures = {url: count for url, count in self.failures.items() if url in urls}
        shown = []
        for url in urls:
            failures[url] = next_count(failures.get(url, 0))
            if failures[url] in FIBONACCI:
                shown.append(url)
        return Backoff(failures), shown


def next_count(count: int) -> int:
    count += 1
    return 1 if count >= FIBONACCI[-1] else count
