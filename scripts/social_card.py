"""Render docs/images/social-card.png (1200x630) for og:image from the tray menu screenshot.

Run it with `just social-card`, then commit the PNG. The offscreen platform keeps the
output the same on any machine.
"""

import os
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import QRect, Qt  # noqa: E402
from PySide6.QtGui import QColor, QFont, QImage, QPainter  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

IMAGES = Path(__file__).resolve().parent.parent / "docs" / "images"
WIDTH, HEIGHT, MARGIN = 1200, 630, 70
GREEN = QColor(146, 208, 80)


def draw_text(p: QPainter, rect: QRect, text: str, size: int, bold: bool, color: QColor) -> None:
    font = QFont("Helvetica", size)
    font.setBold(bold)
    p.setFont(font)
    p.setPen(color)
    p.drawText(rect, int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap), text)


def main() -> None:
    _app = QApplication([])
    image = QImage(WIDTH, HEIGHT, QImage.Format.Format_RGB32)
    image.fill(QColor("#1f2933"))
    p = QPainter(image)
    p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(GREEN)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(MARGIN, MARGIN, 90, 90, 22, 22)
    draw_text(p, QRect(MARGIN, 210, 640, 90), "BuildNotify", 54, True, QColor("white"))
    draw_text(p, QRect(MARGIN, 310, 640, 100), "CI build status in your system tray", 26, False, QColor("#cbd2d9"))
    menu = QImage(str(IMAGES / "projectlist.png"))
    menu = menu.scaledToHeight(HEIGHT - 2 * MARGIN, Qt.TransformationMode.SmoothTransformation)
    p.drawImage(WIDTH - MARGIN - menu.width(), (HEIGHT - menu.height()) // 2, menu)
    p.end()
    image.save(str(IMAGES / "social-card.png"))


if __name__ == "__main__":
    main()
