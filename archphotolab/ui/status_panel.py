from __future__ import annotations

from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QWidget

from archphotolab.constants import (
    LABEL_STATUS_PANEL,
)


class StatusPanel(QGroupBox):
    def __init__(self, parent=None) -> None:
        super().__init__(LABEL_STATUS_PANEL, parent)
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        self.lbl_step = QLabel("")
        self.lbl_files = QLabel("")
        self.lbl_points = QLabel("")
        self.lbl_mismatch = QLabel("")
        self.lbl_quality = QLabel("")
        self.lbl_grade = QLabel("")
        self.lbl_guide = QLabel("")
        self.lbl_project = QLabel("")
        self.lbl_message = QLabel("")

        for label in (
            self.lbl_step,
            self.lbl_files,
            self.lbl_points,
            self.lbl_mismatch,
            self.lbl_quality,
            self.lbl_grade,
            self.lbl_guide,
            self.lbl_project,
            self.lbl_message,
        ):
            label.setWordWrap(True)
            layout.addWidget(label)

    def set_texts(self, *, step: str, files: str, points: str, mismatch: str, quality: str, grade: str, guide: str, project: str, message: str) -> None:
        self.lbl_step.setText(step)
        self.lbl_files.setText(files)
        self.lbl_points.setText(points)
        self.lbl_mismatch.setText(mismatch)
        self.lbl_quality.setText(quality)
        self.lbl_grade.setText(grade)
        self.lbl_guide.setText(guide)
        self.lbl_project.setText(project)
        self.lbl_message.setText(message)
