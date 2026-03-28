from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Sequence, Set

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from archphotolab.core.export import export_paths, now_timestamp, save_png
from archphotolab.core.geometry import (
    compute_reprojection_errors,
    estimate_homography,
    mean_and_max_error,
    warp_plan_to_photo,
)
from archphotolab.core.imagery import blend_overlay, flatten_illumination, load_rgb_image
from archphotolab.core.project_io import (
    apply_project_dict_to_state,
    load_project,
    resolve_saved_image_path,
    state_to_dict,
)
from archphotolab.state import AppState


class ImagePanel(QWidget):
    pointAdded = Signal(float, float)
    pointMoved = Signal(int, float, float)
    pointRemoved = Signal(int)
    pointSelected = Signal(int)

    def __init__(self, title: str, editable: bool = True, parent=None) -> None:
        super().__init__(parent)
        self._title = title
        self._editable = editable
        self._image: Optional[np.ndarray] = None
        self._pixmap: Optional[QPixmap] = None
        self._points: list[tuple[float, float]] = []
        self._warning_indices: set[int] = set()
        self._selected_index: Optional[int] = None

        self._dragging_index: Optional[int] = None

        self._display_scale = 1.0
        self._img_left = 0
        self._img_top = 0
        self._img_width = 1
        self._img_height = 1

        self.setMinimumSize(260, 260)
        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)

    def set_title(self, title: str) -> None:
        self._title = title
        self.update()

    def set_image(self, image: Optional[np.ndarray]) -> None:
        self._image = image
        if image is None:
            self._pixmap = None
            self._img_width = 1
            self._img_height = 1
            self.update()
            return

        if image.ndim != 3 or image.shape[2] != 3:
            raise ValueError("이미지는 RGB 형식이어야 합니다.")

        qimg = QImage(
            image.data,
            image.shape[1],
            image.shape[0],
            image.strides[0],
            QImage.Format_RGB888,
        ).copy()
        self._pixmap = QPixmap.fromImage(qimg)
        self._img_width = image.shape[1]
        self._img_height = image.shape[0]
        self._update_draw_geometry()
        self.update()

    def set_points(
        self,
        points: Sequence[tuple[float, float]],
        warning_indices: Optional[set[int]] = None,
        selected_index: Optional[int] = None,
    ) -> None:
        self._points = list(points)
        self._warning_indices = set(warning_indices or [])
        self._selected_index = selected_index
        self.update()

    def set_editable(self, enabled: bool) -> None:
        self._editable = enabled

    def _update_draw_geometry(self) -> None:
        if self._pixmap is None:
            return
        target_h = max(1, self.height() - 40)
        target_w = self.width()
        pix = self._pixmap.scaled(
            target_w,
            target_h,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self._display_scale = pix.width() / max(self._img_width, 1)
        self._img_left = (self.width() - pix.width()) // 2
        self._img_top = 28 + (target_h - pix.height()) // 2

    def _from_widget_to_image(self, x: float, y: float) -> Optional[tuple[float, float]]:
        if self._pixmap is None:
            return None
        img_x = (x - self._img_left) / self._display_scale
        img_y = (y - self._img_top) / self._display_scale
        if img_x < 0 or img_y < 0 or img_x > self._img_width or img_y > self._img_height:
            return None
        return float(img_x), float(img_y)

    def _to_widget_from_image(self, point: tuple[float, float]) -> Optional[tuple[int, int]]:
        if self._pixmap is None:
            return None
        return (
            self._img_left + int(round(point[0] * self._display_scale)),
            self._img_top + int(round(point[1] * self._display_scale)),
        )

    def _find_point_at(self, widget_x: float, widget_y: float) -> Optional[int]:
        if self._pixmap is None:
            return None
        if self._from_widget_to_image(widget_x, widget_y) is None:
            return None

        wx = widget_x - self._img_left
        wy = widget_y - self._img_top
        radius = max(8.0, 10.0 / max(self._display_scale, 1e-6))
        radius = min(radius, 12.0)

        for idx, (x, y) in enumerate(self._points):
            sx = x * self._display_scale
            sy = y * self._display_scale
            if (sx - wx) ** 2 + (sy - wy) ** 2 <= radius ** 2:
                return idx
        return None

    def mousePressEvent(self, event) -> None:
        if not self._editable or self._pixmap is None:
            return

        idx = self._find_point_at(event.position().x(), event.position().y())
        if event.button() == Qt.LeftButton:
            if idx is None:
                point = self._from_widget_to_image(event.position().x(), event.position().y())
                if point is not None:
                    self.pointAdded.emit(point[0], point[1])
            else:
                self._selected_index = idx
                self._dragging_index = idx
                self.pointSelected.emit(idx)
                self.update()

    def mouseMoveEvent(self, event) -> None:
        if not self._editable or self._pixmap is None or self._dragging_index is None:
            return
        if not event.buttons() & Qt.LeftButton:
            return

        point = self._from_widget_to_image(event.position().x(), event.position().y())
        if point is not None:
            self.pointMoved.emit(self._dragging_index, point[0], point[1])

    def mouseReleaseEvent(self, event) -> None:
        self._dragging_index = None
        event.accept()

    def mouseDoubleClickEvent(self, event) -> None:
        if not self._editable or self._pixmap is None:
            return
        if event.button() == Qt.LeftButton:
            idx = self._find_point_at(event.position().x(), event.position().y())
            if idx is not None:
                self.pointRemoved.emit(idx)
                self._dragging_index = None
                self._selected_index = None

    def resizeEvent(self, event) -> None:
        self._update_draw_geometry()
        super().resizeEvent(event)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(43, 61, 88))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor(107, 140, 177))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        painter.fillRect(0, 0, self.width(), 28, QColor(31, 43, 64))

        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.setPen(QColor(224, 233, 248))
        painter.drawText(8, 20, self._title)

        if self._pixmap is None:
            painter.setPen(QColor(180, 188, 205))
            painter.setFont(QFont("", 10))
            painter.drawText(16, self.height() // 2, "이미지를 불러와 주세요")
            return

        pix = self._pixmap.scaled(
            self.width(),
            max(1, self.height() - 40),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self._display_scale = pix.width() / max(self._img_width, 1)
        self._img_left = (self.width() - pix.width()) // 2
        self._img_top = 28 + (max(1, self.height() - 40) - pix.height()) // 2
        painter.drawPixmap(self._img_left, self._img_top, pix)

        for idx, point in enumerate(self._points):
            widget_point = self._to_widget_from_image(point)
            if widget_point is None:
                continue
            px, py = widget_point
            if idx in self._warning_indices:
                brush = QColor(255, 99, 99)
            elif idx == self._selected_index:
                brush = QColor(255, 196, 0)
            else:
                brush = QColor(106, 140, 255)

            painter.setPen(QPen(QColor(20, 20, 24), 1))
            painter.setBrush(brush)
            painter.drawEllipse(px - 9, py - 9, 18, 18)
            painter.setPen(QColor(24, 24, 24))
            painter.setFont(QFont("", 9))
            painter.drawText(px + 2, py + 4, str(idx + 1))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("ArchPhotoLab")
        self._palette = {
            "primary": "#151d2b",
            "secondary": "#23304a",
            "accent": "#6a8cff",
            "text": "#e6edf7",
            "muted": "#96a9c1",
            "panel": "#2b3d58",
            "danger": "#ff8f8f",
        }

        self.state = AppState()
        self._selected_point_side = "photo"
        self._point_mode_enabled = True
        self.last_dir = str(Path.home())
        self._warn_threshold = 12.0
        self._intro_visible = True

        self._build_ui()
        self._apply_theme()
        self._refresh_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(8)

        intro_box = QGroupBox("첫 사용 가이드")
        intro_box.setObjectName("IntroCard")
        intro_layout = QVBoxLayout(intro_box)
        self.lbl_intro = QLabel(
            "실행 순서: "
            "1) 드론 사진 불러오기 → 2) 도면 불러오기 → "
            "3) 양쪽에 대응점 찍기(양쪽 각 4개 이상) → 4) 자동 정합 → "
            "5) 정합 overlay 확인 및 투명도 조절 → 6) 플랫 보정 적용 비교 → "
            "7) PNG 저장(overlay / 평탄화 / 정합 도면)"
        )
        self.lbl_intro.setWordWrap(True)
        intro_layout.addWidget(self.lbl_intro)

        self.btn_toggle_intro = QPushButton("안내 숨기기")
        self.btn_toggle_intro.setCheckable(True)
        self.btn_toggle_intro.setChecked(True)
        self.btn_toggle_intro.toggled.connect(self._toggle_intro)
        intro_layout.addWidget(self.btn_toggle_intro, alignment=Qt.AlignRight)

        # 워크플로 버튼
        controls = QVBoxLayout()
        controls.setSpacing(8)

        row1 = QHBoxLayout()
        row1.setSpacing(8)
        self.btn_open_photo = QPushButton("사진 불러오기")
        self.btn_open_plan = QPushButton("도면 불러오기")
        self.btn_load_project = QPushButton("프로젝트 불러오기")
        self.btn_save_project = QPushButton("결과 저장")

        self.btn_open_photo.clicked.connect(self._load_photo)
        self.btn_open_plan.clicked.connect(self._load_plan)
        self.btn_load_project.clicked.connect(self._load_project)
        self.btn_save_project.clicked.connect(self._save_project)

        row1.addWidget(self.btn_open_photo)
        row1.addWidget(self.btn_open_plan)
        row1.addWidget(self.btn_load_project)
        row1.addWidget(self.btn_save_project)
        row1.addStretch()

        row2 = QHBoxLayout()
        row2.setSpacing(8)
        self.btn_point_mode = QPushButton("대응점 찍기 시작")
        self.btn_point_mode.setCheckable(True)
        self.btn_point_mode.setChecked(True)
        self.btn_point_mode.toggled.connect(self._toggle_point_mode)

        self.btn_align = QPushButton("자동 정합")
        self.btn_align.clicked.connect(self._run_alignment)

        self.btn_flatten = QPushButton("플랫 보정 적용")
        self.btn_flatten.clicked.connect(self._apply_flatten)

        self.chk_compare_flat = QCheckBox("원본/평탄화 보기")
        self.chk_compare_flat.toggled.connect(self._toggle_flat_compare)

        self.btn_delete_point = QPushButton("점 다시 맞추기")
        self.btn_delete_point.clicked.connect(self._clear_selected_point)

        self.btn_export = QPushButton("PNG 내보내기")
        self.btn_export.clicked.connect(self._export_pngs)

        row2.addWidget(self.btn_point_mode)
        row2.addWidget(self.btn_align)
        row2.addWidget(self.btn_flatten)
        row2.addWidget(self.chk_compare_flat)
        row2.addWidget(self.btn_delete_point)
        row2.addWidget(self.btn_export)
        row2.addStretch()

        self._apply_control_style(
            self.btn_open_photo,
            self.btn_open_plan,
            self.btn_load_project,
            self.btn_save_project,
            self.btn_point_mode,
            self.btn_align,
            self.btn_flatten,
            self.btn_delete_point,
            self.btn_export,
        )

        row3 = QHBoxLayout()
        row3.setSpacing(10)
        row3.addWidget(QLabel("보기 모드"))
        self.cmb_view = QComboBox()
        self.cmb_view.addItem("사진만", "photo")
        self.cmb_view.addItem("도면만", "plan")
        self.cmb_view.addItem("정합 overlay", "overlay")
        self.cmb_view.currentIndexChanged.connect(self._on_view_mode_changed)

        row3.addWidget(self.cmb_view)
        row3.addWidget(QLabel("도면 투명도"))
        self.slider_alpha = QSlider(Qt.Horizontal)
        self.slider_alpha.setRange(0, 100)
        self.slider_alpha.setValue(int(self.state.overlay_alpha * 100))
        self.slider_alpha.valueChanged.connect(self._on_alpha_changed)
        self.lbl_alpha = QLabel(f"{int(self.state.overlay_alpha * 100)}%")
        self.slider_alpha.setMinimumWidth(160)
        self.cmb_view.setMinimumWidth(140)
        row3.addWidget(self.slider_alpha)
        row3.addWidget(self.lbl_alpha)
        row3.addStretch()

        controls.addLayout(row1)
        controls.addLayout(row2)
        controls.addLayout(row3)

        # 패널 3개 구성
        panels = QHBoxLayout()
        self.photo_panel, self.photo_view, self.photo_info = self._create_panel("드론 사진")
        self.plan_panel, self.plan_view, self.plan_info = self._create_panel("도면")
        self.result_panel, self.result_view, self.result_info = self._create_panel("결과 표시", editable=False)
        self.photo_panel.setObjectName("WorkPanel")
        self.plan_panel.setObjectName("WorkPanel")
        self.result_panel.setObjectName("WorkPanel")

        panels.addWidget(self.photo_panel, 1)
        panels.addWidget(self.plan_panel, 1)
        panels.addWidget(self.result_panel, 1)

        # 상태 표시 영역
        state_box = QGroupBox("상태")
        state_box.setObjectName("StatusPanel")
        state_box_layout = QVBoxLayout(state_box)
        self.lbl_step = QLabel("현재 단계: 사진 불러오기")
        self.lbl_files = QLabel("사진: 없음 / 도면: 없음")
        self.lbl_points = QLabel("대응점: 사진 0개 / 도면 0개")
        self.lbl_mismatch = QLabel("")
        self.lbl_quality = QLabel("정합 품질: 계산 전")
        self.lbl_guide = QLabel("워크플로: 사진 불러오기 → 도면 불러오기 → 대응점 4개 이상 추가")
        self.lbl_project = QLabel("마지막 저장: 없음")
        self.lbl_message = QLabel("")

        for label in (
            self.lbl_step,
            self.lbl_files,
            self.lbl_points,
            self.lbl_mismatch,
            self.lbl_quality,
            self.lbl_guide,
            self.lbl_project,
            self.lbl_message,
        ):
            label.setWordWrap(True)
            state_box_layout.addWidget(label)

        self.photo_view.pointAdded.connect(lambda x, y: self._on_point_added("photo", x, y))
        self.plan_view.pointAdded.connect(lambda x, y: self._on_point_added("plan", x, y))

        self.photo_view.pointMoved.connect(lambda i, x, y: self._on_point_moved("photo", i, x, y))
        self.photo_view.pointRemoved.connect(lambda i: self._on_point_removed("photo", i))
        self.photo_view.pointSelected.connect(lambda i: self._on_point_selected("photo", i))

        self.plan_view.pointMoved.connect(lambda i, x, y: self._on_point_moved("plan", i, x, y))
        self.plan_view.pointRemoved.connect(lambda i: self._on_point_removed("plan", i))
        self.plan_view.pointSelected.connect(lambda i: self._on_point_selected("plan", i))

        root_layout.addWidget(intro_box)
        root_layout.addLayout(controls)
        root_layout.addLayout(panels, stretch=9)
        root_layout.addWidget(state_box)

    def _apply_control_style(self, *widgets: QPushButton) -> None:
        for widget in widgets:
            widget.setMinimumHeight(34)
            widget.setMinimumWidth(130)
            widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    def _apply_theme(self) -> None:
        pal = self._palette
        self.setStyleSheet(
            f"""
            QWidget {{
                color: {pal["text"]};
                font-family: "Pretendard", "Apple SD Gothic Neo", "Malgun Gothic", "Segoe UI", sans-serif;
                font-size: 10.5pt;
            }}
            QMainWindow {{
                background: {pal["primary"]};
            }}
            QGroupBox {{
                background: {pal["secondary"]};
                border: 1px solid {pal["accent"]}44;
                border-radius: 12px;
                margin-top: 10px;
                padding: 8px 10px 10px 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 0 6px;
                color: {pal["accent"]};
                font-weight: 700;
            }}
            QPushButton {{
                background: {pal["panel"]};
                border: 1px solid {pal["accent"]}66;
                border-radius: 9px;
                padding: 7px 12px;
                font-weight: 700;
                min-width: 130px;
                min-height: 34px;
            }}
            QPushButton:hover {{
                background: {pal["accent"]}22;
                border-color: {pal["accent"]};
            }}
            QPushButton:checked {{
                background: {pal["accent"]}44;
            }}
            QPushButton:pressed {{
                background: {pal["accent"]}33;
            }}
            QPushButton:disabled {{
                background: {pal["primary"]};
                border-color: {pal["panel"]};
                color: {pal["muted"]};
            }}
            QComboBox {{
                background: {pal["panel"]};
                border: 1px solid {pal["accent"]}55;
                border-radius: 8px;
                min-height: 24px;
                min-width: 140px;
                padding: 4px 10px;
            }}
            QComboBox QAbstractItemView {{
                background: {pal["secondary"]};
                selection-background-color: {pal["accent"]}55;
                color: {pal["text"]};
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {pal["accent"]}55;
                height: 8px;
                border-radius: 4px;
                background: {pal["panel"]};
            }}
            QSlider::sub-page:horizontal {{
                background: {pal["accent"]};
                border-radius: 4px;
            }}
            QSlider::add-page:horizontal {{
                background: {pal["panel"]};
            }}
            QSlider::handle:horizontal {{
                background: {pal["accent"]};
                border: 1px solid {pal["accent"]}cc;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }}
            QCheckBox {{
                spacing: 6px;
                color: {pal["text"]};
            }}
            #IntroCard {{
                background: {pal["secondary"]};
            }}
            #StatusPanel, #WorkPanel {{
                background: {pal["secondary"]};
                border: 1px solid {pal["accent"]}22;
            }}
            QMessageBox {{
                color: {pal["primary"]};
            }}
            """,
        )

    def _toggle_intro(self, checked: bool) -> None:
        self._intro_visible = checked
        self.lbl_intro.setVisible(checked)
        self.btn_toggle_intro.setText("안내 숨기기" if checked else "안내 보기")

    def _create_panel(self, title: str, editable: bool = True):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel(title)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        header.setFont(font)
        header.setStyleSheet(f"padding: 4px 2px; color: {self._palette['text']};")

        view = ImagePanel(title=title, editable=editable)
        info = QLabel("이미지 없음")
        info.setWordWrap(True)
        info.setStyleSheet(f"padding: 2px 4px; color: {self._palette['muted']};")

        layout.addWidget(header)
        layout.addWidget(view, stretch=1)
        layout.addWidget(info)
        return container, view, info

    def _toggle_point_mode(self, enabled: bool) -> None:
        self._point_mode_enabled = enabled
        self.photo_view.set_editable(enabled)
        self.plan_view.set_editable(enabled)
        self._set_message("점 편집 모드: 사용" if enabled else "점 편집 모드: 잠금")

    def _on_view_mode_changed(self) -> None:
        self.state.result_view_mode = self._current_view_mode()
        self._refresh_result_view()

    def _current_view_mode(self) -> str:
        return str(self.cmb_view.currentData())

    def _on_alpha_changed(self, value: int) -> None:
        self.state.overlay_alpha = value / 100.0
        self.lbl_alpha.setText(f"{value}%")
        self._refresh_result_view()

    def _toggle_flat_compare(self, checked: bool) -> None:
        if checked:
            if self.state.photo_image is None:
                self.chk_compare_flat.setChecked(False)
                self._set_message("원본/평탄화 보기를 하려면 먼저 사진을 불러와야 합니다.", is_error=True)
                return

            if self.state.flattened_photo is None:
                try:
                    self.state.flattened_photo = flatten_illumination(self.state.photo_image)
                except Exception as exc:
                    self.chk_compare_flat.setChecked(False)
                    self._set_message(f"평탄화 계산 실패: {exc}", is_error=True)
                    return

            self.state.show_flat_photo = True
        else:
            self.state.show_flat_photo = False

        self._refresh_ui()

    def _effective_photo_image(self) -> Optional[np.ndarray]:
        if self.state.show_flat_photo and self.state.flattened_photo is not None:
            return self.state.flattened_photo
        return self.state.photo_image

    def _on_point_added(self, side: str, x: float, y: float) -> None:
        if not self._point_mode_enabled:
            return

        image = self.state.photo_image if side == "photo" else self.state.plan_image
        if image is None:
            return

        point = (
            max(0.0, min(float(x), image.shape[1] - 1)),
            max(0.0, min(float(y), image.shape[0] - 1)),
        )

        if side == "photo":
            self.state.photo_points.append(point)
            self.state.selected_photo_point = len(self.state.photo_points) - 1
            self.state.selected_plan_point = None
            self._selected_point_side = "photo"
        else:
            self.state.plan_points.append(point)
            self.state.selected_plan_point = len(self.state.plan_points) - 1
            self.state.selected_photo_point = None
            self._selected_point_side = "plan"

        self.state.clear_alignment()
        self._set_message(f"{side} 대응점 {len(self.state.photo_points) if side == 'photo' else len(self.state.plan_points)}개 추가")
        self._refresh_ui()

    def _on_point_moved(self, side: str, index: int, x: float, y: float) -> None:
        if not self._point_mode_enabled:
            return

        points = self.state.photo_points if side == "photo" else self.state.plan_points
        image = self.state.photo_image if side == "photo" else self.state.plan_image
        if index < 0 or index >= len(points) or image is None:
            return

        points[index] = (
            max(0.0, min(float(x), image.shape[1] - 1)),
            max(0.0, min(float(y), image.shape[0] - 1)),
        )

        if side == "photo":
            self.state.selected_photo_point = index
            self.state.selected_plan_point = None
            self._selected_point_side = "photo"
        else:
            self.state.selected_plan_point = index
            self.state.selected_photo_point = None
            self._selected_point_side = "plan"

        self.state.clear_alignment()
        self._refresh_point_overlays()

    def _on_point_removed(self, side: str, index: int) -> None:
        if not self._point_mode_enabled:
            return

        points = self.state.photo_points if side == "photo" else self.state.plan_points
        if index < 0 or index >= len(points):
            return

        del points[index]
        if side == "photo":
            self.state.selected_photo_point = None
        else:
            self.state.selected_plan_point = None

        self._selected_point_side = side
        self.state.clear_alignment()
        self._refresh_ui()

    def _on_point_selected(self, side: str, index: int) -> None:
        self._selected_point_side = side
        if side == "photo":
            self.state.selected_photo_point = index
            self.state.selected_plan_point = None
        else:
            self.state.selected_plan_point = index
            self.state.selected_photo_point = None
        self._refresh_point_overlays()

    def _clear_selected_point(self) -> None:
        if self._selected_point_side == "photo" and self.state.selected_photo_point is not None:
            self._on_point_removed("photo", self.state.selected_photo_point)
            self._set_message("선택한 사진 대응점을 삭제했습니다.")
            return

        if self.state.selected_plan_point is not None:
            self._on_point_removed("plan", self.state.selected_plan_point)
            self._set_message("선택한 도면 대응점을 삭제했습니다.")
            return

        self._set_message("삭제할 점을 선택하세요.", is_error=True)

    def _load_photo(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "드론 사진 불러오기",
            self.last_dir,
            "PNG/JPG 이미지 (*.png *.jpg *.jpeg)",
        )
        if not file_path:
            return

        try:
            image = load_rgb_image(file_path)
            self.state.photo_path = file_path
            self.state.photo_image = image
            self.state.photo_points = []
            self.state.selected_photo_point = None
            self.state.flattened_photo = None
            self.state.show_flat_photo = False
            self.chk_compare_flat.setChecked(False)
            self.state.clear_alignment()
            self.last_dir = str(Path(file_path).parent)
            self._set_message(f"사진 로드: {Path(file_path).name}")
            self._refresh_ui()
        except Exception as exc:
            QMessageBox.warning(self, "오류", f"사진을 열지 못했습니다.\n{exc}")
            self._set_message(f"사진 로드 실패: {exc}", is_error=True)

    def _load_plan(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "도면 불러오기",
            self.last_dir,
            "PNG/JPG 이미지 (*.png *.jpg *.jpeg)",
        )
        if not file_path:
            return

        try:
            image = load_rgb_image(file_path)
            self.state.plan_path = file_path
            self.state.plan_image = image
            self.state.plan_points = []
            self.state.selected_plan_point = None
            self.state.clear_alignment()
            self.last_dir = str(Path(file_path).parent)
            self._set_message(f"도면 로드: {Path(file_path).name}")
            self._refresh_ui()
        except Exception as exc:
            QMessageBox.warning(self, "오류", f"도면을 열지 못했습니다.\n{exc}")
            self._set_message(f"도면 로드 실패: {exc}", is_error=True)

    def _run_alignment(self) -> None:
        if self.state.photo_image is None or self.state.plan_image is None:
            self._set_message("정합은 사진과 도면을 모두 불러온 뒤에 가능합니다.", is_error=True)
            return

        min_points = min(len(self.state.photo_points), len(self.state.plan_points))
        if min_points < 4:
            self._set_message("자동 정합은 양쪽 모두에서 4개 이상의 대응점이 필요합니다.", is_error=True)
            return

        homography, err, _ = estimate_homography(self.state.photo_points, self.state.plan_points)
        if homography is None:
            self.state.clear_alignment()
            self.state.warped_plan = None
            self._set_message(f"정합 실패: {err}", is_error=True)
            self._refresh_ui()
            return

        if len(self.state.photo_points) != len(self.state.plan_points):
            self._set_message("경고: 대응점 개수가 다릅니다. 앞쪽의 공통 개수만 사용해 정렬합니다.", is_error=False)

        try:
            self.state.homography = homography
            self.state.warped_plan = warp_plan_to_photo(
                self.state.plan_image,
                homography,
                self.state.photo_image.shape,
            )

            self.state.reprojection_errors = compute_reprojection_errors(
                self.state.photo_points,
                self.state.plan_points,
                homography,
            )
            self.state.reprojection_avg, self.state.reprojection_max = mean_and_max_error(
                self.state.reprojection_errors,
            )
            self.state.homography = homography
            self._set_message(
                f"자동 정합 완료: 평균 {self.state.reprojection_avg:.2f}px, 최대 {self.state.reprojection_max:.2f}px",
            )
        except Exception as exc:
            self.state.clear_alignment()
            self.state.warped_plan = None
            self._set_message(f"정합 후 결과 계산 실패: {exc}", is_error=True)

        self._refresh_ui()

    def _apply_flatten(self) -> None:
        if self.state.photo_image is None:
            self._set_message("평탄화할 사진이 없습니다.", is_error=True)
            return

        try:
            self.state.flattened_photo = flatten_illumination(self.state.photo_image)
            self.state.show_flat_photo = True
            self.chk_compare_flat.setChecked(True)
            self._set_message("플랫 보정 적용됨")
            self._refresh_ui()
        except Exception as exc:
            self._set_message(f"평탄화 실패: {exc}", is_error=True)

    def _export_pngs(self) -> None:
        if self.state.photo_image is None:
            self._set_message("출력할 사진이 없어 내보내기할 수 없습니다.", is_error=True)
            return

        if self.state.warped_plan is None and len(self.state.photo_points) >= 4 and len(self.state.plan_points) >= 4:
            self._run_alignment()

        output_dir = QFileDialog.getExistingDirectory(self, "내보낼 폴더 선택", self.last_dir)
        if not output_dir:
            return

        self.last_dir = str(Path(output_dir))

        try:
            overlay_path, flat_path, warped_path = export_paths(output_dir, now_timestamp())

            flat_image = self.state.flattened_photo
            if flat_image is None:
                flat_image = flatten_illumination(self.state.photo_image)
            save_png(flat_path, flat_image)

            saved = [f"flat: {Path(flat_path).name}"]
            missing: list[str] = []

            if self.state.warped_plan is not None:
                save_png(warped_path, self.state.warped_plan)
                saved.append(f"warped plan: {Path(warped_path).name}")

                overlay = self._compose_overlay()
                save_png(overlay_path, overlay)
                saved.append(f"overlay: {Path(overlay_path).name}")
            else:
                missing.append("정합 overlay")
                missing.append("도면 정합 결과")

            message = "\n".join(saved)
            if missing:
                message += "\n\n누락: " + ", ".join(missing)

            QMessageBox.information(
                self,
                "저장 완료",
                f"저장된 파일:\n{message}\n\n폴더: {output_dir}",
            )
            self._set_message(f"PNG 내보내기 완료: {output_dir}")
        except Exception as exc:
            self._set_message(f"PNG 내보내기 실패: {exc}", is_error=True)
            QMessageBox.warning(self, "오류", f"PNG 저장 실패\n{exc}")

    def _compose_overlay(self) -> np.ndarray:
        base = self._effective_photo_image()
        if base is None:
            raise ValueError("기준 사진이 없습니다.")
        if self.state.warped_plan is None:
            raise ValueError("정합 결과가 없습니다.")
        return blend_overlay(base, self.state.warped_plan, self.state.overlay_alpha)

    def _save_project(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "프로젝트 저장",
            self.last_dir,
            "ArchPhotoLab 프로젝트 (*.json)",
        )
        if not file_path:
            return
        if not file_path.lower().endswith(".json"):
            file_path += ".json"

        self.last_dir = str(Path(file_path).parent)
        payload = state_to_dict(self.state)
        payload["photo_path"] = self.state.photo_path
        payload["plan_path"] = self.state.plan_path
        payload["format_version"] = "1.0"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        self.state.last_project_file = file_path
        self._set_message(f"프로젝트 저장 완료: {file_path}")
        QMessageBox.information(self, "저장", f"프로젝트를 저장했습니다.\n{file_path}")
        self._refresh_ui()

    def _load_project(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "프로젝트 불러오기",
            self.last_dir,
            "ArchPhotoLab 프로젝트 (*.json)",
        )
        if not file_path:
            return

        self.last_dir = str(Path(file_path).parent)

        try:
            loaded = apply_project_dict_to_state(load_project(file_path))
            self.state = loaded
            self.state.last_project_file = file_path

            missing: list[str] = []

            if self.state.photo_path:
                resolved = resolve_saved_image_path(self.state.photo_path, file_path, [self.last_dir])
                if resolved:
                    self.state.photo_path = resolved
                    self.state.photo_image = load_rgb_image(resolved)
                else:
                    self.state.photo_path = self.state.photo_path
                    self.state.photo_image = None
                    self.state.photo_points = []
                    missing.append("드론 사진")

            if self.state.plan_path:
                resolved = resolve_saved_image_path(self.state.plan_path, file_path, [self.last_dir])
                if resolved:
                    self.state.plan_path = resolved
                    self.state.plan_image = load_rgb_image(resolved)
                else:
                    self.state.plan_path = self.state.plan_path
                    self.state.plan_image = None
                    self.state.plan_points = []
                    missing.append("도면")

            if (
                self.state.homography is not None
                and self.state.photo_image is not None
                and self.state.plan_image is not None
            ):
                self.state.warped_plan = warp_plan_to_photo(
                    self.state.plan_image,
                    self.state.homography,
                    self.state.photo_image.shape,
                )
                self.state.reprojection_errors = compute_reprojection_errors(
                    self.state.photo_points,
                    self.state.plan_points,
                    self.state.homography,
                )
                self.state.reprojection_avg, self.state.reprojection_max = mean_and_max_error(
                    self.state.reprojection_errors,
                )
            else:
                self.state.homography = None
                self.state.warped_plan = None

            if self.state.show_flat_photo and self.state.photo_image is not None:
                self.state.flattened_photo = flatten_illumination(self.state.photo_image)

            self.slider_alpha.setValue(int(self.state.overlay_alpha * 100))
            self.chk_compare_flat.setChecked(self.state.show_flat_photo)
            self._set_combo_by_value(self.state.result_view_mode)

            msg = f"프로젝트를 불러왔습니다: {Path(file_path).name}"
            if missing:
                msg += f"\n경고: {', '.join(missing)} 경로를 찾지 못했습니다."

            self._set_message(msg)
            self._refresh_ui()
        except Exception as exc:
            self._set_message(f"프로젝트 불러오기 실패: {exc}", is_error=True)
            QMessageBox.warning(self, "오류", f"프로젝트를 열지 못했습니다.\n{exc}")

    def _set_combo_by_value(self, value: str) -> None:
        for i in range(self.cmb_view.count()):
            if self.cmb_view.itemData(i) == value:
                self.cmb_view.setCurrentIndex(i)
                return

    def _refresh_ui(self) -> None:
        self._sync_controls()
        self._refresh_panel_images()
        self._refresh_point_overlays()
        self._refresh_result_view()
        self._refresh_status()

    def _sync_controls(self) -> None:
        self.photo_view.set_editable(self._point_mode_enabled)
        self.plan_view.set_editable(self._point_mode_enabled)
        can_align = (
            self.state.photo_image is not None
            and self.state.plan_image is not None
            and len(self.state.photo_points) >= 4
            and len(self.state.plan_points) >= 4
            and len(self.state.photo_points) == len(self.state.plan_points)
        )
        self.btn_align.setEnabled(can_align)
        self.btn_align.setToolTip(
            "양쪽 이미지에서 대응점을 동일 개수로 4개 이상 찍어야 자동 정합이 가능합니다."
            if not can_align
            else "현재 점으로 정합을 계산합니다."
        )
        self.btn_delete_point.setEnabled(
            self.state.selected_photo_point is not None or self.state.selected_plan_point is not None,
        )
        self.btn_flatten.setEnabled(self.state.photo_image is not None)
        self.slider_alpha.setEnabled(self.state.warped_plan is not None)
        self.btn_export.setEnabled(self.state.photo_image is not None)

    def _refresh_panel_images(self) -> None:
        if self.state.photo_image is None:
            self.photo_view.set_image(None)
            self.photo_info.setText("사진: 없음")
        else:
            self.photo_view.set_image(self._effective_photo_image())
            name = Path(self.state.photo_path).name if self.state.photo_path else "임시"
            self.photo_info.setText(
                f"사진: {name} ({self.state.photo_image.shape[1]} x {self.state.photo_image.shape[0]})",
            )

        if self.state.plan_image is None:
            self.plan_view.set_image(None)
            self.plan_info.setText("도면: 없음")
        else:
            self.plan_view.set_image(self.state.plan_image)
            name = Path(self.state.plan_path).name if self.state.plan_path else "임시"
            self.plan_info.setText(
                f"도면: {name} ({self.state.plan_image.shape[1]} x {self.state.plan_image.shape[0]})",
            )

    def _point_warning_indices(self, threshold: float | None = None) -> Set[int]:
        if threshold is None:
            threshold = self._warn_threshold
        bad: Set[int] = set()
        for idx, value in enumerate(self.state.reprojection_errors):
            if value > threshold:
                bad.add(idx)
        return bad

    def _refresh_point_overlays(self) -> None:
        warning = self._point_warning_indices()
        self.photo_view.set_points(
            self.state.photo_points,
            warning_indices=warning,
            selected_index=self.state.selected_photo_point,
        )
        self.plan_view.set_points(
            self.state.plan_points,
            warning_indices=warning,
            selected_index=self.state.selected_plan_point,
        )

    def _refresh_result_view(self) -> None:
        mode = self._current_view_mode()
        self.state.result_view_mode = mode

        if mode == "photo":
            image = self._effective_photo_image()
            info = "결과 표시: 사진만"
        elif mode == "plan":
            image = self.state.plan_image
            info = "결과 표시: 도면만"
        else:
            if self.state.photo_image is None:
                image = None
                info = "결과 표시: 정합 overlay (사진 없음)"
            elif self.state.warped_plan is None:
                image = self._effective_photo_image()
                info = "결과 표시: 정합 overlay (정합 미실행)"
            else:
                image = self._compose_overlay()
                info = "결과 표시: 정합 overlay"

        self.result_view.set_image(image)
        self.result_info.setText(info)

    def _refresh_status(self) -> None:
        photo_name = Path(self.state.photo_path).name if self.state.photo_path else "없음"
        plan_name = Path(self.state.plan_path).name if self.state.plan_path else "없음"
        self.lbl_files.setText(f"사진: {photo_name} / 도면: {plan_name}")
        self.lbl_points.setText(f"대응점: 사진 {len(self.state.photo_points)}개 / 도면 {len(self.state.plan_points)}개")

        if len(self.state.photo_points) != len(self.state.plan_points):
            self.lbl_mismatch.setText("경고: 대응점 개수 불일치")
            self.lbl_mismatch.setStyleSheet(f"color: {self._palette['danger']};")
        else:
            self.lbl_mismatch.setText("")
            self.lbl_mismatch.setStyleSheet("color: transparent;")

        if self.state.reprojection_avg is None:
            self.lbl_quality.setText("정합 품질: 계산 전")
        else:
            warn_count = len(self._point_warning_indices())
            self.lbl_quality.setText(
                f"정합 품질: 평균 오차 {self.state.reprojection_avg:.2f}px / 최대 오차 {self.state.reprojection_max:.2f}px "
                f"(오차 큰 점: {warn_count}개)",
            )
            self.lbl_quality.setStyleSheet(f"color: {self._palette['text']};")

        if self.state.last_project_file:
            self.lbl_project.setText(f"마지막 저장: {self.state.last_project_file}")
        else:
            self.lbl_project.setText("마지막 저장: 없음")

        if self.state.photo_image is None:
            self.lbl_step.setText("현재 단계: 사진 불러오기")
            self.lbl_guide.setText("워크플로: 1) 사진을 불러오고, 2) 도면을 불러오세요.")
        elif self.state.plan_image is None:
            self.lbl_step.setText("현재 단계: 도면 불러오기")
            self.lbl_guide.setText("워크플로: 1) 도면을 불러온 뒤, 2) 사진·도면에 대응점을 찍으세요.")
        elif len(self.state.photo_points) < 4 or len(self.state.plan_points) < 4:
            self.lbl_step.setText("현재 단계: 대응점 찍기")
            self.lbl_guide.setText("워크플로: 양쪽 이미지에 대응점을 각각 최소 4개씩 찍어야 정합을 계산할 수 있습니다.")
        elif self.state.homography is None:
            self.lbl_step.setText("현재 단계: 자동 정합")
            if len(self.state.photo_points) != len(self.state.plan_points):
                self.lbl_guide.setText("경고: 대응점 개수가 달라 자동 정합 버튼이 비활성입니다. 양쪽 개수를 맞춰주세요.")
            else:
                self.lbl_guide.setText("정합 준비 완료. 정합 버튼을 눌러 overlay 미리보기를 확인하세요.")
        else:
            self.lbl_step.setText("현재 단계: overlay 확인")
            self.lbl_guide.setText("정합 완료. 도면 투명도를 조절하고, 필요하면 점을 수정해 다시 정합한 뒤 PNG 내보내기를 진행하세요.")

    def _set_message(self, text: str, is_error: bool = False) -> None:
        self.lbl_message.setText(text)
        self.lbl_message.setStyleSheet(
            f"color: {self._palette['danger'] if is_error else self._palette['text']};",
        )
