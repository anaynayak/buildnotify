from dataclasses import replace

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QTabWidget, QVBoxLayout, QWidget

from buildnotifylib.core.ports import Connection
from buildnotifylib.core.settings import AppSettings
from buildnotifylib.ui.dialogs.preferences.advanced_page import AdvancedChoices, AdvancedPage
from buildnotifylib.ui.dialogs.preferences.menu_page import MenuChoices, MenuPage
from buildnotifylib.ui.dialogs.preferences.notifications_page import NotificationChoices, NotificationsPage
from buildnotifylib.ui.dialogs.preferences.servers_page import ServersPage

LAST_BUILD_TIME = "lastBuildTimeForProject"


class PreferencesDialog(QDialog):
    def __init__(
        self,
        settings: AppSettings,
        connection: Connection,
        parent: QWidget | None = None,
        keystore_available: bool = True,
    ):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle(self.tr("Preferences"))
        self.servers_page = ServersPage(settings.timeout_seconds, connection, keystore_available)
        self.notifications_page = NotificationsPage()
        self.menu_page = MenuPage()
        self.advanced_page = AdvancedPage()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.servers_page, self.tr("Servers"))
        self.tabs.addTab(self.menu_page, self.tr("Menu"))
        self.tabs.addTab(self.notifications_page, self.tr("Notifications"))
        self.tabs.addTab(self.advanced_page, self.tr("Advanced"))
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)
        layout.addWidget(self.button_box)
        self.set_value(settings)

    def set_value(self, settings: AppSettings) -> None:
        self.servers_page.set_value(settings.servers)
        events = {key: settings.notify(key) for key in self.notifications_page.events}
        self.notifications_page.set_value(
            NotificationChoices(events, settings.custom_script, settings.custom_script_enabled)
        )
        self.menu_page.set_value(
            MenuChoices(
                settings.notify(LAST_BUILD_TIME),
                settings.show_last_build_label,
                settings.symbolic_icons,
                settings.sort_key,
            )
        )
        self.advanced_page.set_value(AdvancedChoices(settings.interval_seconds, settings.timeout_seconds))

    def edited_settings(self) -> AppSettings:
        notifications = self.notifications_page.value()
        menu = self.menu_page.value()
        advanced = self.advanced_page.value()
        return replace(
            self.settings,
            servers=self.servers_page.value(),
            interval_seconds=advanced.interval_seconds,
            timeout_seconds=advanced.timeout_seconds,
            custom_script=notifications.script,
            custom_script_enabled=notifications.script_enabled,
            sort_key=menu.sort_key,
            show_last_build_label=menu.show_last_build_label,
            symbolic_icons=menu.symbolic_icons,
            notifications={**notifications.events, LAST_BUILD_TIME: menu.show_last_build_time},
        )

    def open(self) -> AppSettings | None:  # type: ignore
        if self.exec() == QDialog.DialogCode.Accepted:
            return self.edited_settings()
        return None
