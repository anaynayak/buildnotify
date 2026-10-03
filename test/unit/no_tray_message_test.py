from buildnotifylib.core.no_tray_message import no_tray_message


def test_should_name_the_appindicator_extension_on_gnome():
    message = no_tray_message("ubuntu:GNOME")

    assert "BuildNotify needs a system tray." in message
    assert "AppIndicator" in message


def test_should_not_mention_gnome_elsewhere():
    message = no_tray_message("KDE")

    assert "BuildNotify needs a system tray." in message
    assert "AppIndicator" not in message


def test_should_cope_with_an_unset_desktop():
    assert "AppIndicator" not in no_tray_message(None)
