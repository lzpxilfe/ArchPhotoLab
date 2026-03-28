from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QTimer, qInstallMessageHandler
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QSplashScreen, QMessageBox

from archphotolab.constants import (
    APP_ICON_FILE,
    APP_NAME,
    DEFAULT_WINDOW_SIZE,
    DIALOG_TITLE_ERROR,
    PYTHON_LOG_FORMAT,
    MSG_FATAL_LOG_PREFIX,
    SPLASH_BG_COLOR,
    SPLASH_BODY_FONT_SIZE,
    SPLASH_DURATION_MS,
    SPLASH_ICON_MAX_SIZE,
    SPLASH_ICON_TOP_MARGIN,
    SPLASH_MESSAGE_LINES,
    SPLASH_TEXT_COLOR,
    SPLASH_TITLE,
    SPLASH_TITLE_BAR_HEIGHT,
    SPLASH_TITLE_FONT_SIZE,
    SPLASH_TEXT_HEIGHT,
    SPLASH_TEXT_LEFT,
    SPLASH_TEXT_TOP_OFFSET,
    SPLASH_TEXT_WIDTH_MARGIN,
    SPLASH_TEXT_Y_ICON_FAILED,
    SPLASH_TEXT_Y_NO_ICON,
    SPLASH_TEXT_Y_WITH_ICON_OFFSET,
    SPLASH_WIDTH,
    SPLASH_HEIGHT,
)
from archphotolab.ui.main_window import MainWindow


logging.basicConfig(level=logging.INFO, format=PYTHON_LOG_FORMAT)
LOGGER = logging.getLogger(__name__)


def _qt_message_handler(mode, context, message):
    # Keep Qt internal logs visible but non-fatal.
    LOGGER.debug("Qt: %s", message)


def _show_error_dialog(exc: Exception) -> None:
    """Show a simple error dialog for uncaught exceptions while keeping logs."""
    QMessageBox.critical(None, DIALOG_TITLE_ERROR, f"{type(exc).__name__}: {exc}")


def _app_icon_path() -> Optional[Path]:
    icon_path = Path(__file__).resolve().parent / APP_ICON_FILE
    return icon_path if icon_path.exists() else None


def _startup_splash(app: QApplication) -> Optional[QSplashScreen]:
    icon_path = _app_icon_path()
    width = SPLASH_WIDTH
    height = SPLASH_HEIGHT

    pix = QPixmap(width, height)
    pix.fill(QColor(*SPLASH_BG_COLOR))

    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)

    title_font = QFont()
    title_font.setPointSize(SPLASH_TITLE_FONT_SIZE)
    title_font.setBold(True)

    body_font = QFont()
    body_font.setPointSize(SPLASH_BODY_FONT_SIZE)

    if icon_path is not None:
        icon = QPixmap(str(icon_path))
        if not icon.isNull():
            icon = icon.scaled(SPLASH_ICON_MAX_SIZE, SPLASH_ICON_MAX_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x = (width - icon.width()) // 2
            painter.drawPixmap(x, SPLASH_ICON_TOP_MARGIN, icon)
            y_text = icon.height() + SPLASH_TEXT_Y_WITH_ICON_OFFSET
        else:
            y_text = SPLASH_TEXT_Y_ICON_FAILED
    else:
        y_text = SPLASH_TEXT_Y_NO_ICON

    painter.setPen(QColor(*SPLASH_TEXT_COLOR))
    painter.setFont(title_font)
    painter.drawText(0, y_text, width, SPLASH_TITLE_BAR_HEIGHT, Qt.AlignHCenter, SPLASH_TITLE)
    painter.setFont(body_font)
    painter.drawText(
        SPLASH_TEXT_LEFT,
        y_text + SPLASH_TEXT_TOP_OFFSET,
        width - SPLASH_TEXT_WIDTH_MARGIN,
        SPLASH_TEXT_HEIGHT,
        Qt.AlignHCenter | Qt.TextWordWrap,
        "\n".join(SPLASH_MESSAGE_LINES),
    )
    painter.end()

    splash = QSplashScreen(pix)
    splash.show()
    app.processEvents()
    QTimer.singleShot(SPLASH_DURATION_MS, splash.close)
    return splash


def main() -> int:
    qInstallMessageHandler(_qt_message_handler)
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)

    icon_path = _app_icon_path()
    if icon_path is not None:
        icon = QIcon(str(icon_path))
        app.setWindowIcon(icon)

    splash = _startup_splash(app)

    try:
        win = MainWindow()
        if icon_path is not None:
            win.setWindowIcon(QIcon(str(icon_path)))
        win.resize(*DEFAULT_WINDOW_SIZE)
        win.show()
        if splash is not None:
            splash.finish(win)
        return int(app.exec())
    except Exception as exc:  # pragma: no cover - safety fallback
        LOGGER.exception(MSG_FATAL_LOG_PREFIX)
        _show_error_dialog(exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
