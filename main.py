from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QTimer, qInstallMessageHandler
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen, QMessageBox

from archphotolab.ui.main_window import MainWindow


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
LOGGER = logging.getLogger(__name__)


def _qt_message_handler(mode, context, message):
    # Keep Qt internal logs visible but non-fatal.
    LOGGER.debug("Qt: %s", message)


def _show_error_dialog(exc: Exception) -> None:
    """Show a simple error dialog for uncaught exceptions while keeping logs."""
    QMessageBox.critical(None, "오류", f"{type(exc).__name__}: {exc}")


def _app_icon_path() -> Optional[Path]:
    icon_path = Path(__file__).resolve().parent / "icon.png"
    return icon_path if icon_path.exists() else None


def _startup_splash(app: QApplication) -> Optional[QSplashScreen]:
    icon_path = _app_icon_path()
    width = 520
    height = 260

    pix = QPixmap(width, height)
    pix.fill(QColor(24, 28, 38))

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)

    title_font = QFont()
    title_font.setPointSize(15)
    title_font.setBold(True)

    body_font = QFont()
    body_font.setPointSize(10)

    if icon_path is not None:
        icon = QPixmap(str(icon_path))
        if not icon.isNull():
            icon = icon.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x = (width - icon.width()) // 2
            painter.drawPixmap(x, 16, icon)
            y_text = icon.height() + 30
        else:
            y_text = 26
    else:
        y_text = 30

    painter.setPen(QColor(228, 236, 255))
    painter.setFont(title_font)
    painter.drawText(0, y_text, width, 34, Qt.AlignHCenter, "ArchPhotoLab")
    painter.setFont(body_font)
    painter.drawText(
        20,
        y_text + 38,
        width - 40,
        70,
        Qt.AlignHCenter | Qt.TextWordWrap,
        "GNU General Public License 2.0 기반\n"
        "공공에게 공개된 오픈 소스 도구입니다.\n"
        "사진-도면 정합·점 기반 작업 워크플로를 시작합니다.",
    )
    painter.end()

    splash = QSplashScreen(pix)
    splash.show()
    app.processEvents()
    QTimer.singleShot(1400, splash.close)
    return splash


def main() -> int:
    qInstallMessageHandler(_qt_message_handler)
    app = QApplication(sys.argv)
    app.setApplicationName("ArchPhotoLab")
    app.setApplicationDisplayName("ArchPhotoLab")

    icon_path = _app_icon_path()
    if icon_path is not None:
        icon = QIcon(str(icon_path))
        app.setWindowIcon(icon)

    splash = _startup_splash(app)

    try:
        win = MainWindow()
        if icon_path is not None:
            win.setWindowIcon(QIcon(str(icon_path)))
        win.resize(1660, 1020)
        win.show()
        if splash is not None:
            splash.finish(win)
        return int(app.exec())
    except Exception as exc:  # pragma: no cover - safety fallback
        LOGGER.exception("Fatal error during startup")
        _show_error_dialog(exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
