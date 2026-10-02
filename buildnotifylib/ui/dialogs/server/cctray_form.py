from PySide6.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QWidget


class CctrayForm(QWidget):
    """The cctray feed URL."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.url = QLineEdit()
        self.url.setPlaceholderText("http://[host]:[port]/dashboard/cctray.xml")
        self.url_label = QLabel(self.tr("Path to cctray.xml"))
        self.url_label.setBuddy(self.url)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.url_label)
        layout.addWidget(self.url)

    def set_value(self, url: str) -> None:
        self.url.setText(url)

    def value(self) -> str:
        return self.url.text()
