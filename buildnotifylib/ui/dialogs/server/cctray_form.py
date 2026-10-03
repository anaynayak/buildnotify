from PySide6.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QWidget

from buildnotifylib.ui.widgets.forms import MessageLabel


class CctrayForm(QWidget):
    """The cctray feed URL."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.url = QLineEdit()
        self.url.setPlaceholderText("http://[host]:[port]/dashboard/cctray.xml")
        self.url_label = QLabel(self.tr("&Feed URL"))
        self.url_label.setBuddy(self.url)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.url_label)
        layout.addWidget(self.url)
        self.message = MessageLabel()
        layout.addWidget(self.message)
        self.url.editingFinished.connect(self.add_scheme)

    def set_value(self, url: str) -> None:
        self.url.setText(url)

    def value(self) -> str:
        return with_scheme(self.url.text().strip())

    def add_scheme(self) -> None:
        self.url.setText(self.value())


def with_scheme(url: str) -> str:
    return url if url == "" or "://" in url else "https://" + url
