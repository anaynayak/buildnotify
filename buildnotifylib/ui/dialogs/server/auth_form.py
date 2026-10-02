from dataclasses import dataclass

from PySide6.QtWidgets import QComboBox, QGroupBox, QLineEdit, QWidget

from buildnotifylib.core.settings import ServerSettings
from buildnotifylib.ui.widgets.forms import add_row, form_layout


@dataclass(frozen=True)
class Credentials:
    authentication_type: int = ServerSettings.AUTH_USERNAME_PASSWORD
    username: str = ""
    password: str = ""


class AuthForm(QGroupBox):
    """The authentication type, username and password or token of a source."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setTitle(self.tr("Authentication"))
        self.authentication_type = QComboBox()
        self.authentication_type.addItems([self.tr("Username/password"), self.tr("Authentication Bearer token")])
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.form = form_layout()
        add_row(self.form, self.tr("Authentication type"), self.authentication_type)
        self.username_label = add_row(self.form, self.tr("Username"), self.username)
        self.password_label = add_row(self.form, self.tr("Password"), self.password)
        self.setLayout(self.form)

    def set_value(self, credentials: Credentials) -> None:
        self.username.setText(credentials.username)
        self.password.setText(credentials.password)
        self.select_silently(credentials.authentication_type)
        self.show_username(credentials.authentication_type == ServerSettings.AUTH_USERNAME_PASSWORD)

    def value(self) -> Credentials:
        return Credentials(self.authentication_type.currentIndex(), self.username.text(), self.password.text())

    def select_silently(self, index: int) -> None:
        self.authentication_type.blockSignals(True)
        self.authentication_type.setCurrentIndex(index)
        self.authentication_type.blockSignals(False)

    def show_username(self, visible: bool) -> None:
        self.form.setRowVisible(self.username, visible)

    def show_type(self, visible: bool) -> None:
        self.form.setRowVisible(self.authentication_type, visible)

    def show_token_field(self) -> None:
        self.username.setText("")
        self.show_username(False)
        self.password_label.setText(self.tr("Token"))
        self.password.setPlaceholderText(self.tr("Optional for public repositories"))

    def set_authentication_type(self, index: int) -> None:
        self.username.setText("")
        self.password.setText("")
        if ServerSettings.AUTH_USERNAME_PASSWORD == index:
            self.show_username(True)
            self.password_label.setText(self.tr("Password"))
            self.password.setPlaceholderText("")
        elif ServerSettings.AUTH_BEARER_TOKEN == index:
            self.show_username(False)
            self.password_label.setText(self.tr("Bearer token"))
            self.password.setPlaceholderText(self.tr("Do not include the 'Bearer' keyword"))
        else:
            raise NotImplementedError(
                f'Unsupported value: "{self.authentication_type.currentText()}". An implementation is missing.'
            )

    def disable_keyring(self) -> None:
        self.setTitle(self.tr("Authentication (keyring dependency missing)"))
        for widget in (self.authentication_type, self.username, self.password):
            widget.setEnabled(False)
