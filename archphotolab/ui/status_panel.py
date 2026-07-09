from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGroupBox, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QFrame

from archphotolab.constants import (
    LABEL_STATUS_PANEL,
)


class StatusPanel(QGroupBox):
    def __init__(self, parent=None) -> None:
        super().__init__("", parent)
        self._build()

    def _build(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Grid layout for the 4 status cards
        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)

        # Card 1: Project Info
        self.card1 = QFrame()
        self.card1.setProperty("class", "StatusCard")
        c1_layout = QVBoxLayout(self.card1)
        c1_layout.setContentsMargins(12, 10, 12, 10)
        c1_layout.setSpacing(4)
        lbl_c1_title = QLabel("PROJECT STATUS")
        lbl_c1_title.setProperty("class", "CardTitle")
        self.lbl_step = QLabel("")
        self.lbl_step.setProperty("class", "CardValue")
        self.lbl_project = QLabel("")
        self.lbl_project.setProperty("class", "CardSubValue")
        c1_layout.addWidget(lbl_c1_title)
        c1_layout.addWidget(self.lbl_step)
        c1_layout.addWidget(self.lbl_project)
        grid_layout.addWidget(self.card1, 0, 0)

        # Card 2: Data Info
        self.card2 = QFrame()
        self.card2.setProperty("class", "StatusCard")
        c2_layout = QVBoxLayout(self.card2)
        c2_layout.setContentsMargins(12, 10, 12, 10)
        c2_layout.setSpacing(4)
        lbl_c2_title = QLabel("DATA INFO")
        lbl_c2_title.setProperty("class", "CardTitle")
        self.lbl_points = QLabel("")
        self.lbl_points.setProperty("class", "CardValue")
        self.lbl_files = QLabel("")
        self.lbl_files.setProperty("class", "CardSubValue")
        c2_layout.addWidget(lbl_c2_title)
        c2_layout.addWidget(self.lbl_points)
        c2_layout.addWidget(self.lbl_files)
        grid_layout.addWidget(self.card2, 0, 1)

        # Card 3: Alignment Quality
        self.card3 = QFrame()
        self.card3.setProperty("class", "StatusCard")
        c3_layout = QVBoxLayout(self.card3)
        c3_layout.setContentsMargins(12, 10, 12, 10)
        c3_layout.setSpacing(4)
        lbl_c3_title = QLabel("ALIGNMENT QUALITY")
        lbl_c3_title.setProperty("class", "CardTitle")
        self.lbl_grade = QLabel("")
        self.lbl_grade.setProperty("class", "CardValue")
        self.lbl_quality = QLabel("")
        self.lbl_quality.setProperty("class", "CardSubValue")
        c3_layout.addWidget(lbl_c3_title)
        c3_layout.addWidget(self.lbl_grade)
        c3_layout.addWidget(self.lbl_quality)
        grid_layout.addWidget(self.card3, 0, 2)

        # Card 4: System Alerts & Messages
        self.card4 = QFrame()
        self.card4.setProperty("class", "StatusCard")
        c4_layout = QVBoxLayout(self.card4)
        c4_layout.setContentsMargins(12, 10, 12, 10)
        c4_layout.setSpacing(4)
        lbl_c4_title = QLabel("SYSTEM FEEDBACK")
        lbl_c4_title.setProperty("class", "CardTitle")
        self.lbl_message = QLabel("")
        self.lbl_message.setProperty("class", "CardValue")
        self.lbl_mismatch = QLabel("")
        self.lbl_mismatch.setProperty("class", "CardSubValue")
        c4_layout.addWidget(lbl_c4_title)
        c4_layout.addWidget(self.lbl_message)
        c4_layout.addWidget(self.lbl_mismatch)
        grid_layout.addWidget(self.card4, 0, 3)

        main_layout.addLayout(grid_layout)

        # Bottom full-width Guide Card
        self.guide_card = QFrame()
        self.guide_card.setObjectName("StatusCardGuide")
        guide_layout = QHBoxLayout(self.guide_card)
        guide_layout.setContentsMargins(15, 10, 15, 10)
        self.lbl_guide = QLabel("")
        self.lbl_guide.setProperty("class", "GuideValue")
        self.lbl_guide.setWordWrap(True)
        guide_layout.addWidget(self.lbl_guide)
        main_layout.addWidget(self.guide_card)

        # Set default word wraps
        for label in (
            self.lbl_step,
            self.lbl_files,
            self.lbl_points,
            self.lbl_mismatch,
            self.lbl_quality,
            self.lbl_grade,
            self.lbl_project,
            self.lbl_message,
        ):
            label.setWordWrap(True)

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
