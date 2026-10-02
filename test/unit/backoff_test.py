from hypothesis import given
from hypothesis import strategies as st

from buildnotifylib.core.backoff import Backoff


def shown_per_poll(polls):
    backoff, shown = Backoff(), []
    for urls in polls:
        backoff, result = backoff.advance(urls)
        shown.append(result)
    return shown


def test_should_back_off_repeated_connectivity_notifications():
    shown = [urls == ["url"] for urls in shown_per_poll([["url"]] * 8)]

    assert shown == [True, True, True, False, True, False, False, True]


def test_should_restart_the_sequence_after_21_failures():
    shown = shown_per_poll([["url"]] * 22)

    assert [i + 1 for i, urls in enumerate(shown) if urls] == [1, 2, 3, 5, 8, 13, 21, 22]


def test_should_not_share_back_off_state():
    Backoff().advance(["url"])

    assert Backoff().failures == {}


def test_should_reset_back_off_when_server_recovers():
    assert shown_per_poll([["url"]] * 3 + [[], ["url"]])[-1] == ["url"]


def test_should_track_each_url_separately():
    assert shown_per_poll([["a"], ["a"], ["a"], ["a", "b"]])[-1] == ["b"]


@given(st.lists(st.lists(st.sampled_from(["a", "b", "c"]), unique=True), max_size=30), st.sampled_from(["a", "b", "c"]))
def test_first_failure_after_recovery_should_always_show(polls, url):
    backoff = Backoff()
    for urls in polls:
        backoff, _ = backoff.advance(urls)

    backoff, _ = backoff.advance([])
    assert backoff.advance([url])[1] == [url]
