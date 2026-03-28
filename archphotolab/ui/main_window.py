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
from archphotolab.constants import (
    APP_NAME,
    ALPHA_PERCENT_SCALE,
    BUTTON_BORDER_RADIUS,
    BUTTON_FONT_WEIGHT,
    BUTTON_PADDING_X,
    BUTTON_PADDING_Y,
    CHECKBOX_SPACING,
    COMBO_BORDER_WIDTH,
    COMBO_BORDER_RADIUS,
    COMBO_MIN_HEIGHT,
    COMBO_MIN_WIDTH,
    COMBO_PADDING_X,
    COMBO_PADDING_Y,
    CONTROL_MIN_HEIGHT,
    CONTROL_MIN_WIDTH,
    DIALOG_TITLE_ERROR,
    DIALOG_TITLE_INFO,
    DIALOG_TITLE_SAVE_OK,
    ERROR_WARNING_THRESHOLD_PX,
    FILE_SELECT_EXPORT_FOLDER_TITLE,
    FILE_SELECT_PLAN_TITLE,
    FILE_SELECT_PHOTO_TITLE,
    FILE_SELECT_PROJECT_LOAD_TITLE,
    FILE_SELECT_PROJECT_SAVE_TITLE,
    GUIDE_HIDE_TEXT,
    GUIDE_SHOW_TEXT,
    GROUPBOX_BORDER_ALPHA_SUFFIX,
    GROUPBOX_BORDER_RADIUS,
    GROUPBOX_MARGIN_TOP,
    GROUPBOX_PADDING_BOTTOM,
    GROUPBOX_PADDING_LEFT,
    GROUPBOX_PADDING_RIGHT,
    GROUPBOX_PADDING_TOP,
    GROUPBOX_TITLE_BORDER_ALPHA_SUFFIX,
    GROUPBOX_TITLE_LEFT,
    GROUPBOX_TITLE_PADDING_X,
    IMAGE_FILE_FILTER,
    IMAGE_PANEL_BACKGROUND_RGB,
    IMAGE_PANEL_BORDER_RGB,
    IMAGE_PANEL_EMPTY_TEXT,
    IMAGE_PANEL_HINT_TEXT,
    IMAGE_PANEL_HINT_TEXT_RGB,
    IMAGE_PANEL_HINT_X,
    IMAGE_PANEL_HEADER_PADDING,
    IMAGE_PANEL_INFO_PADDING,
    IMAGE_PANEL_TEXT_RGB,
    IMAGE_PANEL_TITLE_BAR_RGB,
    IMAGE_PANEL_TITLE_X,
    JSON_CHARSET_ENCODING,
    INTRO_TITLE,
    LABEL_PHOTO_PANEL,
    LABEL_PLAN_PANEL,
    LABEL_RESULT_PANEL,
    LABEL_OVERLAY_ALPHA,
    LABEL_STATUS_PANEL,
    LABEL_VIEW_MODE,
    MIN_ALIGNMENT_POINTS,
    MIN_PANEL_SIZE,
    MSG_ALIGNMENT_COMPLETE_FMT,
    MSG_ALIGNMENT_ERROR_FMT,
    MSG_ALIGNMENT_POSTPROC_ERROR_FMT,
    MSG_ALIGNMENT_POINT_MISMATCH_WARN,
    MSG_ALIGNMENT_REQUIRE_IMAGES,
    MSG_ALIGNMENT_REQUIRE_POINTS_FMT,
    MSG_ALIGNMENT_READY_TO_ALIGN_FMT,
    MSG_ALIGNMENT_TOOLTIP_FMT,
    MSG_FLATTEN_APPLIED,
    MSG_FLATTEN_CALC_FAIL_FMT,
    MSG_FLATTEN_ERROR_FMT,
    MSG_FLATTEN_REQUIRED,
    MSG_EXPORT_ERROR_FMT,
    MSG_EXPORT_MISSING_OVERLAY,
    MSG_EXPORT_MISSING_PLAN,
    MSG_EXPORT_MISSING_PREFIX,
    MSG_EXPORT_REQUIRE_PHOTO,
    MSG_EXPORT_RESULT_MESSAGE,
    MSG_EXPORT_SAVED_FLAT_FMT,
    MSG_EXPORT_SAVED_OVERLAY_FMT,
    MSG_EXPORT_SAVED_WARPED_FMT,
    MSG_EXPORT_SUCCESS_FMT,
    MSG_IMAGE_RGB_ONLY,
    MSG_LOAD_MISSING_PHOTO,
    MSG_LOAD_MISSING_PLAN,
    MSG_LOAD_PHOTO_ERROR_FMT,
    MSG_LOAD_PLAN_ERROR_FMT,
    MSG_OVERLAY_BASE_MISSING,
    MSG_OVERLAY_PLAN_MISSING,
    MSG_PNG_SAVE_FAIL_FMT,
    MSG_PLAN_FILE_LOADED_FMT,
    MSG_PLAN_LOAD_FAIL_FMT,
    MSG_PHOTO_FILE_LOADED_FMT,
    MSG_PHOTO_LOAD_FAIL_FMT,
    MSG_PROJECT_LOAD_FAIL_FMT,
    MSG_PROJECT_LOADED_FMT,
    MSG_PROJECT_MISSING_PATH_FMT,
    MSG_PROJECT_SAVED_FMT,
    MSG_PROJECT_SAVED_DIALOG_FMT,
    MSG_POINT_ADDED_FMT,
    MSG_POINT_MODE_OFF,
    MSG_POINT_MODE_ON,
    MSG_QUALITY_SUMMARY_FMT,
    MSG_RESULT_VIEW_FMT,
    MSG_RESULT_VIEW_NO_ALIGNMENT_FMT,
    MSG_RESULT_VIEW_NO_PHOTO_FMT,
    MSG_REQUIRES_PHOTO_FOR_FLAT_COMPARE,
    MSG_SELECT_POINT_TO_DELETE,
    MSG_SELECTED_PHOTO_POINT_DELETED,
    MSG_SELECTED_PLAN_POINT_DELETED,
    OVERLAY_ALPHA_MAX,
    OVERLAY_ALPHA_MIN,
    PANEL_IMAGE_STYLE_COLOR_TRANSPARENT,
    PANEL_RENDER_PADDING_BOTTOM,
    PANEL_TOP_BANNER_HEIGHT,
    PANELS_STRETCH,
    PALETTE,
    POINT_HOVER_RADIUS_FALLBACK_SCALE,
    POINT_HOVER_RADIUS_MAX,
    POINT_HOVER_RADIUS_MIN,
    POINT_HOVER_RADIUS_SCALE,
    POINT_LABEL_FONT_SIZE,
    POINT_LABEL_OFFSET_X,
    POINT_LABEL_OFFSET_Y,
    POINT_LABEL_TEXT_RGB,
    POINT_MARK_SIZE,
    POINT_NORMAL_RGB,
    POINT_OUTLINE_RGB,
    POINT_SELECTED_RGB,
    POINT_WARNING_RGB,
    PROJECT_FILE_FILTER,
    QOBJECT_INTRO_CARD,
    QOBJECT_STATUS_PANEL,
    QOBJECT_WORK_PANEL,
    RESULT_LAST_SAVED_NONE,
    RESULT_LAST_SAVED_PREFIX,
    ROOT_LAYOUT_MARGIN,
    ROOT_LAYOUT_SPACING,
    SLIDER_GROOVE_HEIGHT,
    SLIDER_GROOVE_RADIUS,
    SLIDER_HANDLE_MARGIN_Y,
    SLIDER_HANDLE_SIZE,
    SLIDER_MIN_WIDTH,
    STATUS_FILES_PREFIX,
    STATUS_FILES_SEPARATOR,
    STATUS_GUIDE_PREFIX,
    STATUS_MISMATCH_WARNING,
    STATUS_POINTS_PREFIX,
    STATUS_POINTS_SEPARATOR,
    STATUS_POINTS_SUFFIX,
    STATUS_QUALITY_NOT_CALCULATED,
    STATUS_STEP_ALIGNMENT,
    STATUS_STEP_ALIGNMENT_DONE,
    STATUS_STEP_POINTS,
    STATUS_STEP_PREFIX,
    SUPPORTED_PROJECT_EXTENSION,
    TEMP_FILE_NAME,
    UI_FONT_FAMILY,
    UI_FONT_SIZE,
    UI_TITLE_FONT_SIZE,
    UI_TITLE_OFFSET_Y,
    WORKFLOW_INTRO_TEXT,
    WORKFLOW_MODE_OVERLAY,
    WORKFLOW_MODE_PLAN,
    WORKFLOW_MODE_PHOTO,
    WORKFLOW_ROW3_SPACING,
    WORKFLOW_ROW_SPACING,
    WORKFLOW_SECTION_SPACING,
    WORKFLOW_STEP_1_LOAD_PHOTO,
    WORKFLOW_STEP_1_LOAD_PLAN,
    WORKFLOW_STEP_ALIGNMENT_DONE,
    WORKFLOW_STEP_ALIGNMENT_MISMATCH_WARN,
    WORKFLOW_STEP_ALIGNMENT_READY,
    WORKFLOW_STEP_POINTS,
    VIEW_BUTTON_ALIGN,
    VIEW_BUTTON_EXPORT,
    VIEW_BUTTON_FLATTEN,
    VIEW_BUTTON_LOAD_PROJECT,
    VIEW_BUTTON_OPEN_PLAN,
    VIEW_BUTTON_OPEN_PHOTO,
    VIEW_BUTTON_REMOVE_POINT,
    VIEW_BUTTON_SAVE_PROJECT,
    VIEW_BUTTON_START_POINTS,
    VIEW_LABEL_PLAN,
    VIEW_LABEL_PHOTO,
    VIEW_MODE_OVERLAY,
    VIEW_MODE_PLAN,
    VIEW_MODE_PHOTO,
    VIEW_TOGGLE_COMPARE_FLAT,
    ProjectKeys,
    )
from archphotolab.core.project_io import (
    apply_project_dict_to_state,
    load_project,
    PROJECT_FORMAT,
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

        self.setMinimumSize(*MIN_PANEL_SIZE)
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
            raise ValueError(MSG_IMAGE_RGB_ONLY)

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
        target_h = max(1, self.height() - PANEL_RENDER_PADDING_BOTTOM)
        target_w = self.width()
        pix = self._pixmap.scaled(
            target_w,
            target_h,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self._display_scale = pix.width() / max(self._img_width, 1)
        self._img_left = (self.width() - pix.width()) // 2
        self._img_top = PANEL_TOP_BANNER_HEIGHT + (target_h - pix.height()) // 2

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
        radius = max(
            POINT_HOVER_RADIUS_MIN,
            POINT_HOVER_RADIUS_SCALE / max(self._display_scale, POINT_HOVER_RADIUS_FALLBACK_SCALE),
        )
        radius = min(radius, POINT_HOVER_RADIUS_MAX)

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
        painter.fillRect(self.rect(), QColor(*IMAGE_PANEL_BACKGROUND_RGB))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor(*IMAGE_PANEL_BORDER_RGB))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        painter.fillRect(0, 0, self.width(), PANEL_TOP_BANNER_HEIGHT, QColor(*IMAGE_PANEL_TITLE_BAR_RGB))

        title_font = QFont()
        title_font.setPointSize(UI_TITLE_FONT_SIZE)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.setPen(QColor(*IMAGE_PANEL_TEXT_RGB))
        painter.drawText(IMAGE_PANEL_TITLE_X, UI_TITLE_FONT_SIZE + UI_TITLE_OFFSET_Y, self._title)

        if self._pixmap is None:
            painter.setPen(QColor(*IMAGE_PANEL_HINT_TEXT_RGB))
            painter.setFont(QFont("", int(UI_FONT_SIZE)))
            painter.drawText(IMAGE_PANEL_HINT_X, self.height() // 2, IMAGE_PANEL_HINT_TEXT)
            return

        pix = self._pixmap.scaled(
            self.width(),
            max(1, self.height() - PANEL_RENDER_PADDING_BOTTOM),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self._display_scale = pix.width() / max(self._img_width, 1)
        self._img_left = (self.width() - pix.width()) // 2
        self._img_top = PANEL_TOP_BANNER_HEIGHT + (
            max(1, self.height() - PANEL_RENDER_PADDING_BOTTOM) - pix.height()
        ) // 2
        painter.drawPixmap(self._img_left, self._img_top, pix)

        for idx, point in enumerate(self._points):
            widget_point = self._to_widget_from_image(point)
            if widget_point is None:
                continue
            px, py = widget_point
            if idx in self._warning_indices:
                brush = QColor(*POINT_WARNING_RGB)
            elif idx == self._selected_index:
                brush = QColor(*POINT_SELECTED_RGB)
            else:
                brush = QColor(*POINT_NORMAL_RGB)

            painter.setPen(QPen(QColor(*POINT_OUTLINE_RGB), 1))
            painter.setBrush(brush)
            painter.drawEllipse(
                px - POINT_MARK_SIZE,
                py - POINT_MARK_SIZE,
                POINT_MARK_SIZE * 2,
                POINT_MARK_SIZE * 2,
            )
            painter.setPen(QColor(*POINT_LABEL_TEXT_RGB))
            painter.setFont(QFont("", POINT_LABEL_FONT_SIZE))
            painter.drawText(px + POINT_LABEL_OFFSET_X, py + POINT_LABEL_OFFSET_Y, str(idx + 1))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self._palette = PALETTE

        self.state = AppState()
        self._selected_point_side = VIEW_MODE_PHOTO
        self._point_mode_enabled = True
        self.last_dir = str(Path.home())
        self._warn_threshold = ERROR_WARNING_THRESHOLD_PX
        self._intro_visible = True

        self._build_ui()
        self._apply_theme()
        self._refresh_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(
            ROOT_LAYOUT_MARGIN,
            ROOT_LAYOUT_MARGIN,
            ROOT_LAYOUT_MARGIN,
            ROOT_LAYOUT_MARGIN,
        )
        root_layout.setSpacing(ROOT_LAYOUT_SPACING)

        intro_box = QGroupBox(INTRO_TITLE)
        intro_box.setObjectName(QOBJECT_INTRO_CARD)
        intro_layout = QVBoxLayout(intro_box)
        self.lbl_intro = QLabel(WORKFLOW_INTRO_TEXT)
        self.lbl_intro.setWordWrap(True)
        intro_layout.addWidget(self.lbl_intro)

        self.btn_toggle_intro = QPushButton(GUIDE_HIDE_TEXT)
        self.btn_toggle_intro.setCheckable(True)
        self.btn_toggle_intro.setChecked(True)
        self.btn_toggle_intro.toggled.connect(self._toggle_intro)
        intro_layout.addWidget(self.btn_toggle_intro, alignment=Qt.AlignRight)

        # 워크플로 버튼
        controls = QVBoxLayout()
        controls.setSpacing(WORKFLOW_SECTION_SPACING)

        row1 = QHBoxLayout()
        row1.setSpacing(WORKFLOW_ROW_SPACING)
        self.btn_open_photo = QPushButton(VIEW_BUTTON_OPEN_PHOTO)
        self.btn_open_plan = QPushButton(VIEW_BUTTON_OPEN_PLAN)
        self.btn_load_project = QPushButton(VIEW_BUTTON_LOAD_PROJECT)
        self.btn_save_project = QPushButton(VIEW_BUTTON_SAVE_PROJECT)

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
        row2.setSpacing(WORKFLOW_ROW_SPACING)
        self.btn_point_mode = QPushButton(VIEW_BUTTON_START_POINTS)
        self.btn_point_mode.setCheckable(True)
        self.btn_point_mode.setChecked(True)
        self.btn_point_mode.toggled.connect(self._toggle_point_mode)

        self.btn_align = QPushButton(VIEW_BUTTON_ALIGN)
        self.btn_align.clicked.connect(self._run_alignment)

        self.btn_flatten = QPushButton(VIEW_BUTTON_FLATTEN)
        self.btn_flatten.clicked.connect(self._apply_flatten)

        self.chk_compare_flat = QCheckBox(VIEW_TOGGLE_COMPARE_FLAT)
        self.chk_compare_flat.toggled.connect(self._toggle_flat_compare)

        self.btn_delete_point = QPushButton(VIEW_BUTTON_REMOVE_POINT)
        self.btn_delete_point.clicked.connect(self._clear_selected_point)

        self.btn_export = QPushButton(VIEW_BUTTON_EXPORT)
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
        row3.setSpacing(WORKFLOW_ROW3_SPACING)
        row3.addWidget(QLabel(LABEL_VIEW_MODE))
        self.cmb_view = QComboBox()
        self.cmb_view.addItem(WORKFLOW_MODE_PHOTO, VIEW_MODE_PHOTO)
        self.cmb_view.addItem(WORKFLOW_MODE_PLAN, VIEW_MODE_PLAN)
        self.cmb_view.addItem(WORKFLOW_MODE_OVERLAY, VIEW_MODE_OVERLAY)
        self.cmb_view.currentIndexChanged.connect(self._on_view_mode_changed)

        row3.addWidget(self.cmb_view)
        row3.addWidget(QLabel(LABEL_OVERLAY_ALPHA))
        self.slider_alpha = QSlider(Qt.Horizontal)
        self.slider_alpha.setRange(OVERLAY_ALPHA_MIN, OVERLAY_ALPHA_MAX)
        self.slider_alpha.setValue(int(self.state.overlay_alpha * ALPHA_PERCENT_SCALE))
        self.slider_alpha.valueChanged.connect(self._on_alpha_changed)
        self.lbl_alpha = QLabel(f"{int(self.state.overlay_alpha * ALPHA_PERCENT_SCALE)}%")
        self.slider_alpha.setMinimumWidth(SLIDER_MIN_WIDTH)
        self.cmb_view.setMinimumWidth(COMBO_MIN_WIDTH)
        row3.addWidget(self.slider_alpha)
        row3.addWidget(self.lbl_alpha)
        row3.addStretch()

        controls.addLayout(row1)
        controls.addLayout(row2)
        controls.addLayout(row3)

        # 패널 3개 구성
        panels = QHBoxLayout()
        self.photo_panel, self.photo_view, self.photo_info = self._create_panel(LABEL_PHOTO_PANEL)
        self.plan_panel, self.plan_view, self.plan_info = self._create_panel(LABEL_PLAN_PANEL)
        self.result_panel, self.result_view, self.result_info = self._create_panel(
            LABEL_RESULT_PANEL,
            editable=False,
        )
        self.photo_panel.setObjectName(QOBJECT_WORK_PANEL)
        self.plan_panel.setObjectName(QOBJECT_WORK_PANEL)
        self.result_panel.setObjectName(QOBJECT_WORK_PANEL)

        panels.addWidget(self.photo_panel, 1)
        panels.addWidget(self.plan_panel, 1)
        panels.addWidget(self.result_panel, 1)

        # 상태 표시 영역
        state_box = QGroupBox(LABEL_STATUS_PANEL)
        state_box.setObjectName(QOBJECT_STATUS_PANEL)
        state_box_layout = QVBoxLayout(state_box)
        self.lbl_step = QLabel(f"{STATUS_STEP_PREFIX}{VIEW_BUTTON_OPEN_PHOTO}")
        self.lbl_files = QLabel(
            f"{STATUS_FILES_PREFIX}{INFO_NO_FILE}{STATUS_FILES_SEPARATOR}{VIEW_LABEL_PLAN}: {INFO_NO_FILE}",
        )
        self.lbl_points = QLabel(
            f"{STATUS_POINTS_PREFIX}0{STATUS_POINTS_SEPARATOR}0{STATUS_POINTS_SUFFIX}",
        )
        self.lbl_mismatch = QLabel("")
        self.lbl_quality = QLabel(STATUS_QUALITY_NOT_CALCULATED)
        self.lbl_guide = QLabel(
            f"{STATUS_GUIDE_PREFIX}{WORKFLOW_STEP_1_LOAD_PHOTO}",
        )
        self.lbl_project = QLabel(RESULT_LAST_SAVED_NONE)
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

        self.photo_view.pointAdded.connect(lambda x, y: self._on_point_added(VIEW_MODE_PHOTO, x, y))
        self.plan_view.pointAdded.connect(lambda x, y: self._on_point_added(VIEW_MODE_PLAN, x, y))

        self.photo_view.pointMoved.connect(lambda i, x, y: self._on_point_moved(VIEW_MODE_PHOTO, i, x, y))
        self.photo_view.pointRemoved.connect(lambda i: self._on_point_removed(VIEW_MODE_PHOTO, i))
        self.photo_view.pointSelected.connect(lambda i: self._on_point_selected(VIEW_MODE_PHOTO, i))

        self.plan_view.pointMoved.connect(lambda i, x, y: self._on_point_moved(VIEW_MODE_PLAN, i, x, y))
        self.plan_view.pointRemoved.connect(lambda i: self._on_point_removed(VIEW_MODE_PLAN, i))
        self.plan_view.pointSelected.connect(lambda i: self._on_point_selected(VIEW_MODE_PLAN, i))

        root_layout.addWidget(intro_box)
        root_layout.addLayout(controls)
        root_layout.addLayout(panels, stretch=PANELS_STRETCH)
        root_layout.addWidget(state_box)

    def _apply_control_style(self, *widgets: QPushButton) -> None:
        for widget in widgets:
            widget.setMinimumHeight(CONTROL_MIN_HEIGHT)
            widget.setMinimumWidth(CONTROL_MIN_WIDTH)
            widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    def _apply_theme(self) -> None:
        pal = self._palette
        self.setStyleSheet(
            f"""
            QWidget {{
                color: {pal["text"]};
                font-family: {UI_FONT_FAMILY};
                font-size: {UI_FONT_SIZE}pt;
            }}
            QMainWindow {{
                background: {pal["primary"]};
            }}
            QGroupBox {{
                background: {pal["secondary"]};
                border: 1px solid {pal["accent"]}{GROUPBOX_BORDER_ALPHA_SUFFIX};
                border-radius: {GROUPBOX_BORDER_RADIUS}px;
                margin-top: {GROUPBOX_MARGIN_TOP}px;
                padding: {GROUPBOX_PADDING_TOP}px {GROUPBOX_PADDING_RIGHT}px {GROUPBOX_PADDING_BOTTOM}px {GROUPBOX_PADDING_LEFT}px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: {GROUPBOX_TITLE_LEFT}px;
                padding: 0 {GROUPBOX_TITLE_PADDING_X}px;
                color: {pal["accent"]};
                font-weight: {BUTTON_FONT_WEIGHT};
            }}
            QPushButton {{
                background: {pal["panel"]};
                border: 1px solid {pal["accent"]}{GROUPBOX_TITLE_BORDER_ALPHA_SUFFIX};
                border-radius: {BUTTON_BORDER_RADIUS}px;
                padding: {BUTTON_PADDING_Y}px {BUTTON_PADDING_X}px;
                font-weight: {BUTTON_FONT_WEIGHT};
                min-width: {CONTROL_MIN_WIDTH}px;
                min-height: {CONTROL_MIN_HEIGHT}px;
            }}
            QPushButton:hover {{
                background: {pal["accent"]}{GROUPBOX_BORDER_ALPHA_SUFFIX};
                border-color: {pal["accent"]};
            }}
            QPushButton:checked {{
                background: {pal["accent"]}{GROUPBOX_TITLE_BORDER_ALPHA_SUFFIX};
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
                border: {COMBO_BORDER_WIDTH}px solid {pal["accent"]}55;
                border-radius: {COMBO_BORDER_RADIUS}px;
                min-height: {COMBO_MIN_HEIGHT}px;
                min-width: {COMBO_MIN_WIDTH}px;
                padding: {COMBO_PADDING_Y}px {COMBO_PADDING_X}px;
            }}
            QComboBox QAbstractItemView {{
                background: {pal["secondary"]};
                selection-background-color: {pal["accent"]}55;
                color: {pal["text"]};
            }}
            QSlider::groove:horizontal {{
                border: 1px solid {pal["accent"]}55;
                height: {SLIDER_GROOVE_HEIGHT}px;
                border-radius: {SLIDER_GROOVE_RADIUS}px;
                background: {pal["panel"]};
            }}
            QSlider::sub-page:horizontal {{
                background: {pal["accent"]};
                border-radius: {SLIDER_GROOVE_RADIUS}px;
            }}
            QSlider::add-page:horizontal {{
                background: {pal["panel"]};
            }}
            QSlider::handle:horizontal {{
                background: {pal["accent"]};
                border: 1px solid {pal["accent"]}cc;
                width: {SLIDER_HANDLE_SIZE}px;
                height: {SLIDER_HANDLE_SIZE}px;
                margin: {SLIDER_HANDLE_MARGIN_Y}px 0;
                border-radius: {SLIDER_HANDLE_SIZE // 2}px;
            }}
            QCheckBox {{
                spacing: {CHECKBOX_SPACING}px;
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
        self.btn_toggle_intro.setText(GUIDE_HIDE_TEXT if checked else GUIDE_SHOW_TEXT)

    def _create_panel(self, title: str, editable: bool = True):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel(title)
        font = QFont()
        font.setPointSize(UI_TITLE_FONT_SIZE)
        font.setBold(True)
        header.setFont(font)
        header.setStyleSheet(f"padding: {IMAGE_PANEL_HEADER_PADDING}; color: {self._palette['text']};")

        view = ImagePanel(title=title, editable=editable)
        info = QLabel(IMAGE_PANEL_EMPTY_TEXT)
        info.setWordWrap(True)
        info.setStyleSheet(f"padding: {IMAGE_PANEL_INFO_PADDING}; color: {self._palette['muted']};")

        layout.addWidget(header)
        layout.addWidget(view, stretch=1)
        layout.addWidget(info)
        return container, view, info

    def _toggle_point_mode(self, enabled: bool) -> None:
        self._point_mode_enabled = enabled
        self.photo_view.set_editable(enabled)
        self.plan_view.set_editable(enabled)
        self._set_message(MSG_POINT_MODE_ON if enabled else MSG_POINT_MODE_OFF)

    def _on_view_mode_changed(self) -> None:
        self.state.result_view_mode = self._current_view_mode()
        self._refresh_result_view()

    def _current_view_mode(self) -> str:
        return str(self.cmb_view.currentData())

    def _on_alpha_changed(self, value: int) -> None:
        self.state.overlay_alpha = value / float(ALPHA_PERCENT_SCALE)
        self.lbl_alpha.setText(f"{value}%")
        self._refresh_result_view()

    def _toggle_flat_compare(self, checked: bool) -> None:
        if checked:
            if self.state.photo_image is None:
                self.chk_compare_flat.setChecked(False)
                self._set_message(MSG_REQUIRES_PHOTO_FOR_FLAT_COMPARE, is_error=True)
                return

            if self.state.flattened_photo is None:
                try:
                    self.state.flattened_photo = flatten_illumination(self.state.photo_image)
                except Exception as exc:
                    self.chk_compare_flat.setChecked(False)
                    self._set_message(MSG_FLATTEN_CALC_FAIL_FMT.format(error=exc), is_error=True)
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

        image = self.state.photo_image if side == VIEW_MODE_PHOTO else self.state.plan_image
        if image is None:
            return

        point = (
            max(0.0, min(float(x), image.shape[1] - 1)),
            max(0.0, min(float(y), image.shape[0] - 1)),
        )

        if side == VIEW_MODE_PHOTO:
            self.state.photo_points.append(point)
            self.state.selected_photo_point = len(self.state.photo_points) - 1
            self.state.selected_plan_point = None
            self._selected_point_side = VIEW_MODE_PHOTO
        else:
            self.state.plan_points.append(point)
            self.state.selected_plan_point = len(self.state.plan_points) - 1
            self.state.selected_photo_point = None
            self._selected_point_side = VIEW_MODE_PLAN

        self.state.clear_alignment()
        side_label = VIEW_LABEL_PHOTO if side == VIEW_MODE_PHOTO else VIEW_LABEL_PLAN
        self._set_message(
            MSG_POINT_ADDED_FMT.format(
                side=side_label,
                count=len(self.state.photo_points)
                if side == VIEW_MODE_PHOTO
                else len(self.state.plan_points),
            )
        )
        self._refresh_ui()

    def _on_point_moved(self, side: str, index: int, x: float, y: float) -> None:
        if not self._point_mode_enabled:
            return

        points = self.state.photo_points if side == VIEW_MODE_PHOTO else self.state.plan_points
        image = self.state.photo_image if side == VIEW_MODE_PHOTO else self.state.plan_image
        if index < 0 or index >= len(points) or image is None:
            return

        points[index] = (
            max(0.0, min(float(x), image.shape[1] - 1)),
            max(0.0, min(float(y), image.shape[0] - 1)),
        )

        if side == VIEW_MODE_PHOTO:
            self.state.selected_photo_point = index
            self.state.selected_plan_point = None
            self._selected_point_side = VIEW_MODE_PHOTO
        else:
            self.state.selected_plan_point = index
            self.state.selected_photo_point = None
            self._selected_point_side = VIEW_MODE_PLAN

        self.state.clear_alignment()
        self._refresh_point_overlays()

    def _on_point_removed(self, side: str, index: int) -> None:
        if not self._point_mode_enabled:
            return

        points = self.state.photo_points if side == VIEW_MODE_PHOTO else self.state.plan_points
        if index < 0 or index >= len(points):
            return

        del points[index]
        if side == VIEW_MODE_PHOTO:
            self.state.selected_photo_point = None
        else:
            self.state.selected_plan_point = None

        self._selected_point_side = side
        self.state.clear_alignment()
        self._refresh_ui()

    def _on_point_selected(self, side: str, index: int) -> None:
        self._selected_point_side = side
        if side == VIEW_MODE_PHOTO:
            self.state.selected_photo_point = index
            self.state.selected_plan_point = None
        else:
            self.state.selected_plan_point = index
            self.state.selected_photo_point = None
        self._refresh_point_overlays()

    def _clear_selected_point(self) -> None:
        if self._selected_point_side == VIEW_MODE_PHOTO and self.state.selected_photo_point is not None:
            self._on_point_removed(VIEW_MODE_PHOTO, self.state.selected_photo_point)
            self._set_message(MSG_SELECTED_PHOTO_POINT_DELETED)
            return

        if self.state.selected_plan_point is not None:
            self._on_point_removed(VIEW_MODE_PLAN, self.state.selected_plan_point)
            self._set_message(MSG_SELECTED_PLAN_POINT_DELETED)
            return

        self._set_message(MSG_SELECT_POINT_TO_DELETE, is_error=True)

    def _load_photo(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            FILE_SELECT_PHOTO_TITLE,
            self.last_dir,
            IMAGE_FILE_FILTER,
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
            self._set_message(MSG_PHOTO_FILE_LOADED_FMT.format(name=Path(file_path).name))
            self._refresh_ui()
        except Exception as exc:
            QMessageBox.warning(self, DIALOG_TITLE_ERROR, MSG_LOAD_PHOTO_ERROR_FMT.format(error=exc))
            self._set_message(MSG_PHOTO_LOAD_FAIL_FMT.format(error=exc), is_error=True)

    def _load_plan(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            FILE_SELECT_PLAN_TITLE,
            self.last_dir,
            IMAGE_FILE_FILTER,
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
            self._set_message(MSG_PLAN_FILE_LOADED_FMT.format(name=Path(file_path).name))
            self._refresh_ui()
        except Exception as exc:
            QMessageBox.warning(self, DIALOG_TITLE_ERROR, MSG_LOAD_PLAN_ERROR_FMT.format(error=exc))
            self._set_message(MSG_PLAN_LOAD_FAIL_FMT.format(error=exc), is_error=True)

    def _run_alignment(self) -> None:
        if self.state.photo_image is None or self.state.plan_image is None:
            self._set_message(MSG_ALIGNMENT_REQUIRE_IMAGES, is_error=True)
            return

        min_points = min(len(self.state.photo_points), len(self.state.plan_points))
        if min_points < MIN_ALIGNMENT_POINTS:
            self._set_message(MSG_ALIGNMENT_REQUIRE_POINTS_FMT.format(min_points=MIN_ALIGNMENT_POINTS), is_error=True)
            return

        homography, err, _ = estimate_homography(self.state.photo_points, self.state.plan_points)
        if homography is None:
            self.state.clear_alignment()
            self.state.warped_plan = None
            self._set_message(MSG_ALIGNMENT_ERROR_FMT.format(error=err), is_error=True)
            self._refresh_ui()
            return

        if len(self.state.photo_points) != len(self.state.plan_points):
            self._set_message(MSG_ALIGNMENT_POINT_MISMATCH_WARN, is_error=False)

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
            self._set_message(
                MSG_ALIGNMENT_COMPLETE_FMT.format(
                    avg=self.state.reprojection_avg,
                    max=self.state.reprojection_max,
                )
            )
        except Exception as exc:
            self.state.clear_alignment()
            self.state.warped_plan = None
            self._set_message(MSG_ALIGNMENT_POSTPROC_ERROR_FMT.format(error=exc), is_error=True)

        self._refresh_ui()

    def _apply_flatten(self) -> None:
        if self.state.photo_image is None:
            self._set_message(MSG_FLATTEN_REQUIRED, is_error=True)
            return

        try:
            self.state.flattened_photo = flatten_illumination(self.state.photo_image)
            self.state.show_flat_photo = True
            self.chk_compare_flat.setChecked(True)
            self._set_message(MSG_FLATTEN_APPLIED)
            self._refresh_ui()
        except Exception as exc:
            self._set_message(MSG_FLATTEN_ERROR_FMT.format(error=exc), is_error=True)

    def _export_pngs(self) -> None:
        if self.state.photo_image is None:
            self._set_message(MSG_EXPORT_REQUIRE_PHOTO, is_error=True)
            return

        if (
            self.state.warped_plan is None
            and len(self.state.photo_points) >= MIN_ALIGNMENT_POINTS
            and len(self.state.plan_points) >= MIN_ALIGNMENT_POINTS
        ):
            self._run_alignment()

        output_dir = QFileDialog.getExistingDirectory(self, FILE_SELECT_EXPORT_FOLDER_TITLE, self.last_dir)
        if not output_dir:
            return

        self.last_dir = str(Path(output_dir))

        try:
            overlay_path, flat_path, warped_path = export_paths(output_dir, now_timestamp())

            flat_image = self.state.flattened_photo
            if flat_image is None:
                flat_image = flatten_illumination(self.state.photo_image)
            save_png(flat_path, flat_image)

            saved = [MSG_EXPORT_SAVED_FLAT_FMT.format(filename=Path(flat_path).name)]
            missing: list[str] = []

            if self.state.warped_plan is not None:
                save_png(warped_path, self.state.warped_plan)
                saved.append(MSG_EXPORT_SAVED_WARPED_FMT.format(filename=Path(warped_path).name))

                overlay = self._compose_overlay()
                save_png(overlay_path, overlay)
                saved.append(MSG_EXPORT_SAVED_OVERLAY_FMT.format(filename=Path(overlay_path).name))
            else:
                missing.append(MSG_EXPORT_MISSING_OVERLAY)
                missing.append(MSG_EXPORT_MISSING_PLAN)

            message = "\n".join(saved)
            if missing:
                message += "\n\n" + MSG_EXPORT_MISSING_PREFIX + ", ".join(missing)

            QMessageBox.information(
                self,
                DIALOG_TITLE_SAVE_OK,
                MSG_EXPORT_RESULT_MESSAGE.format(message=message, path=output_dir),
            )
            self._set_message(MSG_EXPORT_SUCCESS_FMT.format(path=output_dir))
        except Exception as exc:
            self._set_message(MSG_EXPORT_ERROR_FMT.format(error=exc), is_error=True)
            QMessageBox.warning(self, DIALOG_TITLE_ERROR, MSG_PNG_SAVE_FAIL_FMT.format(error=exc))

    def _compose_overlay(self) -> np.ndarray:
        base = self._effective_photo_image()
        if base is None:
            raise ValueError(MSG_OVERLAY_BASE_MISSING)
        if self.state.warped_plan is None:
            raise ValueError(MSG_OVERLAY_PLAN_MISSING)
        return blend_overlay(base, self.state.warped_plan, self.state.overlay_alpha)

    def _save_project(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            FILE_SELECT_PROJECT_SAVE_TITLE,
            self.last_dir,
            PROJECT_FILE_FILTER,
        )
        if not file_path:
            return
        if not file_path.lower().endswith(SUPPORTED_PROJECT_EXTENSION):
            file_path += SUPPORTED_PROJECT_EXTENSION

        self.last_dir = str(Path(file_path).parent)
        payload = state_to_dict(self.state)
        payload[ProjectKeys.PHOTO_PATH] = self.state.photo_path
        payload[ProjectKeys.PLAN_PATH] = self.state.plan_path
        payload[ProjectKeys.FORMAT_VERSION] = PROJECT_FORMAT

        with open(file_path, "w", encoding=JSON_CHARSET_ENCODING) as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

        self.state.last_project_file = file_path
        self._set_message(MSG_PROJECT_SAVED_FMT.format(path=file_path))
        QMessageBox.information(
            self,
            DIALOG_TITLE_INFO,
            MSG_PROJECT_SAVED_DIALOG_FMT.format(path=file_path),
        )
        self._refresh_ui()

    def _load_project(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            FILE_SELECT_PROJECT_LOAD_TITLE,
            self.last_dir,
            PROJECT_FILE_FILTER,
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
                    missing.append(MSG_LOAD_MISSING_PHOTO)

            if self.state.plan_path:
                resolved = resolve_saved_image_path(self.state.plan_path, file_path, [self.last_dir])
                if resolved:
                    self.state.plan_path = resolved
                    self.state.plan_image = load_rgb_image(resolved)
                else:
                    self.state.plan_path = self.state.plan_path
                    self.state.plan_image = None
                    self.state.plan_points = []
                    missing.append(MSG_LOAD_MISSING_PLAN)

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

            self.slider_alpha.setValue(int(self.state.overlay_alpha * ALPHA_PERCENT_SCALE))
            self.chk_compare_flat.setChecked(self.state.show_flat_photo)
            self._set_combo_by_value(self.state.result_view_mode)

            msg = MSG_PROJECT_LOADED_FMT.format(name=Path(file_path).name)
            if missing:
                msg += f"\n{MSG_PROJECT_MISSING_PATH_FMT.format(paths=', '.join(missing))}"

            self._set_message(msg)
            self._refresh_ui()
        except Exception as exc:
            self._set_message(MSG_PROJECT_LOAD_FAIL_FMT.format(error=exc), is_error=True)
            QMessageBox.warning(self, DIALOG_TITLE_ERROR, MSG_LOAD_PROJECT_ERROR_FMT.format(error=exc))

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
            and len(self.state.photo_points) >= MIN_ALIGNMENT_POINTS
            and len(self.state.plan_points) >= MIN_ALIGNMENT_POINTS
            and len(self.state.photo_points) == len(self.state.plan_points)
        )
        self.btn_align.setEnabled(can_align)
        self.btn_align.setToolTip(
            MSG_ALIGNMENT_TOOLTIP_FMT.format(min_points=MIN_ALIGNMENT_POINTS)
            if not can_align
            else MSG_ALIGNMENT_READY_TO_ALIGN_FMT
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
            self.photo_info.setText(f"{VIEW_LABEL_PHOTO}: {INFO_NO_FILE}")
        else:
            self.photo_view.set_image(self._effective_photo_image())
            name = Path(self.state.photo_path).name if self.state.photo_path else TEMP_FILE_NAME
            self.photo_info.setText(
                f"{VIEW_LABEL_PHOTO}: {name} ({self.state.photo_image.shape[1]} x {self.state.photo_image.shape[0]})",
            )

        if self.state.plan_image is None:
            self.plan_view.set_image(None)
            self.plan_info.setText(f"{VIEW_LABEL_PLAN}: {INFO_NO_FILE}")
        else:
            self.plan_view.set_image(self.state.plan_image)
            name = Path(self.state.plan_path).name if self.state.plan_path else TEMP_FILE_NAME
            self.plan_info.setText(
                f"{VIEW_LABEL_PLAN}: {name} ({self.state.plan_image.shape[1]} x {self.state.plan_image.shape[0]})",
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

        if mode == VIEW_MODE_PHOTO:
            image = self._effective_photo_image()
            info = MSG_RESULT_VIEW_FMT.format(mode=WORKFLOW_MODE_PHOTO)
        elif mode == VIEW_MODE_PLAN:
            image = self.state.plan_image
            info = MSG_RESULT_VIEW_FMT.format(mode=WORKFLOW_MODE_PLAN)
        else:
            if self.state.photo_image is None:
                image = None
                info = MSG_RESULT_VIEW_NO_PHOTO_FMT.format(mode=WORKFLOW_MODE_OVERLAY)
            elif self.state.warped_plan is None:
                image = self._effective_photo_image()
                info = MSG_RESULT_VIEW_NO_ALIGNMENT_FMT.format(mode=WORKFLOW_MODE_OVERLAY)
            else:
                image = self._compose_overlay()
                info = MSG_RESULT_VIEW_FMT.format(mode=WORKFLOW_MODE_OVERLAY)

        self.result_view.set_image(image)
        self.result_info.setText(info)

    def _refresh_status(self) -> None:
        photo_name = Path(self.state.photo_path).name if self.state.photo_path else INFO_NO_FILE
        plan_name = Path(self.state.plan_path).name if self.state.plan_path else INFO_NO_FILE
        self.lbl_files.setText(f"{STATUS_FILES_PREFIX}{photo_name}{STATUS_FILES_SEPARATOR}{VIEW_LABEL_PLAN}: {plan_name}")
        self.lbl_points.setText(
            f"{STATUS_POINTS_PREFIX}{len(self.state.photo_points)}{STATUS_POINTS_SEPARATOR}{len(self.state.plan_points)}{STATUS_POINTS_SUFFIX}",
        )

        if len(self.state.photo_points) != len(self.state.plan_points):
            self.lbl_mismatch.setText(STATUS_MISMATCH_WARNING)
            self.lbl_mismatch.setStyleSheet(f"color: {self._palette['danger']};")
        else:
            self.lbl_mismatch.setText("")
            self.lbl_mismatch.setStyleSheet(f"color: {PANEL_IMAGE_STYLE_COLOR_TRANSPARENT};")

        if self.state.reprojection_avg is None:
            self.lbl_quality.setText(STATUS_QUALITY_NOT_CALCULATED)
        else:
            warn_count = len(self._point_warning_indices())
            self.lbl_quality.setText(
                MSG_QUALITY_SUMMARY_FMT.format(
                    avg=self.state.reprojection_avg,
                    max=self.state.reprojection_max,
                    warn_count=warn_count,
                ),
            )
            self.lbl_quality.setStyleSheet(f"color: {self._palette['text']};")

        if self.state.last_project_file:
            self.lbl_project.setText(f"{RESULT_LAST_SAVED_PREFIX}{self.state.last_project_file}")
        else:
            self.lbl_project.setText(RESULT_LAST_SAVED_NONE)

        if self.state.photo_image is None:
            self.lbl_step.setText(f"{STATUS_STEP_PREFIX}{VIEW_BUTTON_OPEN_PHOTO}")
            self.lbl_guide.setText(f"{STATUS_GUIDE_PREFIX}{WORKFLOW_STEP_1_LOAD_PHOTO}")
        elif self.state.plan_image is None:
            self.lbl_step.setText(f"{STATUS_STEP_PREFIX}{VIEW_BUTTON_OPEN_PLAN}")
            self.lbl_guide.setText(f"{STATUS_GUIDE_PREFIX}{WORKFLOW_STEP_1_LOAD_PLAN}")
        elif len(self.state.photo_points) < MIN_ALIGNMENT_POINTS or len(self.state.plan_points) < MIN_ALIGNMENT_POINTS:
            self.lbl_step.setText(f"{STATUS_STEP_PREFIX}{STATUS_STEP_POINTS}")
            self.lbl_guide.setText(
                f"{STATUS_GUIDE_PREFIX}{WORKFLOW_STEP_POINTS.format(min_points=MIN_ALIGNMENT_POINTS)}",
            )
        elif self.state.homography is None:
            self.lbl_step.setText(f"{STATUS_STEP_PREFIX}{STATUS_STEP_ALIGNMENT}")
            if len(self.state.photo_points) != len(self.state.plan_points):
                self.lbl_guide.setText(WORKFLOW_STEP_ALIGNMENT_MISMATCH_WARN)
            else:
                self.lbl_guide.setText(WORKFLOW_STEP_ALIGNMENT_READY)
        else:
            self.lbl_step.setText(f"{STATUS_STEP_PREFIX}{STATUS_STEP_ALIGNMENT_DONE}")
            self.lbl_guide.setText(WORKFLOW_STEP_ALIGNMENT_DONE)

    def _set_message(self, text: str, is_error: bool = False) -> None:
        self.lbl_message.setText(text)
        self.lbl_message.setStyleSheet(
            f"color: {self._palette['danger'] if is_error else self._palette['text']};",
        )
