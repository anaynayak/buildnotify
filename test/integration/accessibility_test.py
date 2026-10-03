import re

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QAbstractButton, QAbstractSpinBox, QDialog, QDialogButtonBox, QLabel, QWidget

from buildnotifylib.core.settings import AppSettings, ServerSettings, SourceKind
from buildnotifylib.ui.dialogs.preferences.dialog import PreferencesDialog
from buildnotifylib.ui.dialogs.server.dialog import ServerConfigurationDialog
from test.utils import FakeConnection, fake_content

TIMEOUT = 10
MNEMONIC = re.compile(r"&(\w)")


def tab_walk(dialog: QDialog) -> list[QWidget]:
    """The widgets focus lands on, in order, as Tab is pressed from the first stop until it wraps."""
    dialog.show()
    dialog.activateWindow()
    dialog.setFocus()
    dialog.focusNextPrevChild(True)
    first = dialog.focusWidget()
    walked = [first]
    for _ in range(100):
        dialog.focusNextPrevChild(True)
        widget = dialog.focusWidget()
        if widget is first:
            return walked
        walked.append(widget)
    raise AssertionError("focus never wrapped")


def reading_order(widgets: list[QWidget], dialog: QDialog) -> list[tuple[int, int]]:
    return [(w.mapTo(dialog, w.rect().topLeft()).y(), w.mapTo(dialog, w.rect().topLeft()).x()) for w in widgets]


def assert_visual(walked: list[QWidget], dialog: QDialog) -> None:
    rows = reading_order(walked, dialog)
    assert rows == sorted(rows), [(w.objectName() or type(w).__name__, p) for w, p in zip(walked, rows, strict=True)]


def server_dialog(qtbot, server):
    dialog = ServerConfigurationDialog(server, TIMEOUT, FakeConnection(fake_content()))
    qtbot.addWidget(dialog)
    return dialog


def test_should_tab_through_every_cctray_field_in_visual_order(qtbot):
    dialog = server_dialog(qtbot, ServerSettings("http://localhost/cc.xml", username="u", password="p"))
    dialog.advanced.set_expanded(True)
    walked = tab_walk(dialog)
    expected = [
        dialog.source_kind,
        dialog.cctray.url,
        dialog.auth.authentication_type,
        dialog.auth.username,
        dialog.auth.password,
        dialog.timezone,
        dialog.prefix,
        dialog.test_button,
    ]
    for widget in expected:
        assert widget in walked
    assert_visual(walked, dialog)


def test_should_tab_through_every_github_field_in_visual_order(qtbot):
    server = ServerSettings("", kind=SourceKind.GITHUB, repository="o/n")
    dialog = server_dialog(qtbot, server)
    walked = tab_walk(dialog)
    for widget in (
        dialog.source_kind,
        dialog.github.repository,
        dialog.github.workflow,
        dialog.github.branch,
        dialog.auth.password,
        dialog.prefix,
        dialog.test_button,
    ):
        assert widget in walked
    assert_visual(walked, dialog)


@pytest.mark.parametrize("tab", range(4))
def test_should_tab_through_each_preferences_page_in_visual_order(qtbot, tab):
    dialog = PreferencesDialog(AppSettings(servers=[ServerSettings("http://h/cc.xml")]), FakeConnection(""))
    qtbot.addWidget(dialog)
    dialog.tabs.setCurrentIndex(tab)
    walked = tab_walk(dialog)
    page = dialog.tabs.currentWidget()
    on_page = [w for w in walked if page.isAncestorOf(w)]
    focusable = [w for w in page.findChildren(QWidget) if w.isVisible() and w.isEnabled() and w.focusPolicy().value & 1]
    stops = [w for w in focusable if w.parent().focusProxy() is not w and not isinstance(w.parent(), QAbstractSpinBox)]
    assert all(w in on_page for w in stops)
    assert_visual(walked, dialog)


def labelled_texts(dialog: QDialog) -> list[str]:
    """Texts of everything a user can reach by an Alt key on the current page: buddy labels and buttons."""
    labels = [w.text() for w in dialog.findChildren(QLabel) if w.buddy() is not None and w.isVisibleTo(dialog)]
    buttons = [
        w.text()
        for w in dialog.findChildren(QAbstractButton)
        if w.isVisibleTo(dialog) and not isinstance(w.parent(), QDialogButtonBox) and w.text()
    ]
    return labels + buttons


def mnemonics(texts: list[str]) -> list[str]:
    return [found.group(1).lower() if (found := MNEMONIC.search(text)) else "" for text in texts]


def assert_mnemonics(dialog: QDialog, extra: tuple[str, ...] | list[str] = ()) -> None:
    dialog.show()
    texts = labelled_texts(dialog)
    keys = mnemonics(texts)
    assert all(keys), [t for t, k in zip(texts, keys, strict=True) if not k]
    keys += [k for k in mnemonics(list(extra)) if k]
    assert len(keys) == len(set(keys)), sorted(k for k in keys if keys.count(k) > 1)


def box_texts(dialog: QDialog) -> list[str]:
    return [b.text() for b in dialog.findChildren(QDialogButtonBox)[0].buttons()]


def test_should_give_cctray_server_dialog_unique_mnemonics(qtbot):
    dialog = server_dialog(qtbot, ServerSettings("http://localhost/cc.xml", username="u", password="p"))
    assert_mnemonics(dialog, box_texts(dialog))


def test_should_give_github_server_dialog_unique_mnemonics(qtbot):
    dialog = server_dialog(qtbot, ServerSettings("", kind=SourceKind.GITHUB, repository="o/n"))
    assert_mnemonics(dialog, box_texts(dialog))


@pytest.mark.parametrize("tab", range(4))
def test_should_give_each_preferences_page_unique_mnemonics(qtbot, tab):
    dialog = PreferencesDialog(AppSettings(servers=[ServerSettings("http://h/cc.xml")]), FakeConnection(""))
    qtbot.addWidget(dialog)
    dialog.tabs.setCurrentIndex(tab)
    tab_titles = [dialog.tabs.tabText(i) for i in range(dialog.tabs.count())]
    footer = [b.text() for b in dialog.button_box.buttons()]
    assert_mnemonics(dialog, tab_titles + footer)


def has_name(widget: QWidget, dialog: QDialog) -> bool:
    if widget.accessibleName() or (isinstance(widget, QAbstractButton) and widget.text()):
        return True
    return any(label.buddy() is widget for label in dialog.findChildren(QLabel))


def unnamed_stops(dialog: QDialog) -> list[str]:
    """Focusable controls a screen reader would announce with no name: no accessible name, text or buddy label."""
    stops = [
        w
        for w in dialog.findChildren(QWidget)
        if w.isVisibleTo(dialog)
        and w.focusPolicy().value & 1
        and w.focusProxy() is None
        and not isinstance(w.parent(), QAbstractSpinBox)
        and type(w).__name__ not in ("QTabBar", "QScrollBar")
    ]
    unnamed = [w for w in stops if not has_name(w, dialog)]
    return [f"{type(w).__name__}:{getattr(w, 'placeholderText', lambda: '')()}" for w in unnamed]


def test_should_name_every_control_in_the_server_dialog(qtbot):
    dialog = server_dialog(qtbot, ServerSettings("http://localhost/cc.xml", username="u", password="p"))
    dialog.show()
    dialog.show_picker(True)
    assert unnamed_stops(dialog) == []


@pytest.mark.parametrize("tab", range(4))
def test_should_name_every_control_on_each_preferences_page(qtbot, tab):
    dialog = PreferencesDialog(AppSettings(servers=[ServerSettings("http://h/cc.xml")]), FakeConnection(""))
    qtbot.addWidget(dialog)
    dialog.tabs.setCurrentIndex(tab)
    dialog.show()
    assert unnamed_stops(dialog) == []


def shown(qtbot, dialog: QDialog) -> QDialog:
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)
    return dialog


def press(qtbot, widget: QWidget, key: Qt.Key) -> None:
    widget.setFocus()
    qtbot.keyClick(widget, key)


def test_should_save_the_server_dialog_on_enter(qtbot):
    dialog = shown(qtbot, ServerConfigurationDialog(None, TIMEOUT, FakeConnection("")))
    dialog.cctray.url.setText("http://localhost/cc.xml")
    press(qtbot, dialog.cctray.url, Qt.Key.Key_Return)
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_should_cancel_the_server_dialog_on_escape(qtbot):
    dialog = shown(qtbot, ServerConfigurationDialog(None, TIMEOUT, FakeConnection("")))
    dialog.cctray.url.setText("http://localhost/cc.xml")
    press(qtbot, dialog.cctray.url, Qt.Key.Key_Escape)
    assert dialog.result() == QDialog.DialogCode.Rejected


def test_should_not_save_the_server_dialog_on_enter_in_the_test_button_row(qtbot):
    dialog = shown(qtbot, ServerConfigurationDialog(None, TIMEOUT, FakeConnection("")))
    assert dialog.save_button.isDefault()
    assert not dialog.test_button.autoDefault()


def preferences(qtbot):
    settings = AppSettings(servers=[ServerSettings("http://h/cc.xml")])
    return shown(qtbot, PreferencesDialog(settings, FakeConnection("")))


@pytest.mark.parametrize("tab", range(1, 4))
def test_should_save_preferences_on_enter(qtbot, tab):
    dialog = preferences(qtbot)
    dialog.tabs.setCurrentIndex(tab)
    pages = (dialog.menu_page, dialog.notifications_page, dialog.advanced_page)
    field = dict(zip((1, 2, 3), (pages[0].show_last_build_time, pages[1].script, pages[2].interval), strict=True))
    press(qtbot, field[tab], Qt.Key.Key_Return)
    assert dialog.result() == QDialog.DialogCode.Accepted


@pytest.mark.parametrize("tab", range(4))
def test_should_cancel_preferences_on_escape(qtbot, tab):
    dialog = preferences(qtbot)
    dialog.tabs.setCurrentIndex(tab)
    press(qtbot, dialog.tabs.currentWidget(), Qt.Key.Key_Escape)
    assert dialog.result() == QDialog.DialogCode.Rejected
