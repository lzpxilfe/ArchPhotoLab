from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from archphotolab.constants import (
    CONTROL_MIN_HEIGHT,
    CONTROL_MIN_WIDTH,
    POINT_EDITOR_BUTTON_SPACING,
    VIEW_BUTTON_REDO,
    VIEW_BUTTON_REORDER_DOWN,
    VIEW_BUTTON_REORDER_UP,
    VIEW_BUTTON_UNDO,
)


class PointEditorPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.btn_undo = QPushButton(VIEW_BUTTON_UNDO)
        self.btn_redo = QPushButton(VIEW_BUTTON_REDO)
        self.btn_up = QPushButton(VIEW_BUTTON_REORDER_UP)
        self.btn_down = QPushButton(VIEW_BUTTON_REORDER_DOWN)

        for btn in (self.btn_undo, self.btn_redo, self.btn_up, self.btn_down):
            btn.setMinimumHeight(CONTROL_MIN_HEIGHT)
            btn.setMinimumWidth(CONTROL_MIN_WIDTH)

        layout = QHBoxLayout(self)
        layout.setSpacing(POINT_EDITOR_BUTTON_SPACING)
        layout.addWidget(self.btn_undo)
        layout.addWidget(self.btn_redo)
        layout.addWidget(self.btn_up)
        layout.addWidget(self.btn_down)
        layout.addStretch()
