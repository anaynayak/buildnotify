import pytest

from buildnotifylib.core.menu_labels import about_html, labels


@pytest.mark.parametrize(
    ("platform", "preferences", "quit_"),
    [
        ("darwin", "Settings...", "Quit BuildNotify"),
        ("linux", "Preferences...", "Quit BuildNotify"),
        ("win32", "Preferences...", "Exit"),
    ],
)
def test_labels_follow_platform_norms(platform, preferences, quit_):
    found = labels(platform)
    assert (found.preferences, found.about, found.quit) == (preferences, "About BuildNotify", quit_)


def test_about_describes_feeds_and_links_to_project():
    text = about_html("1.2.3")
    assert "cctray" in text and "GitHub Actions" in text
    assert "cruise control" not in text
    assert "https://github.com/anaynayak/buildnotify" in text
