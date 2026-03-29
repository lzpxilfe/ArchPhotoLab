from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
)

from archphotolab.constants import (
    APP_NAME,
    ALIGNMENT_MODE_AFFINE,
    ALIGNMENT_MODE_HOMOGRAPHY,
    ALIGNMENT_MODE_LABELS,
    ALIGNMENT_MODE_SIMILARITY,
    ALPHA_PERCENT_SCALE,
    BUTTON_BORDER_RADIUS,
    BUTTON_FONT_WEIGHT,
    BUTTON_PADDING_X,
    BUTTON_PADDING_Y,
    CHECKBOX_SPACING,
    COMBO_BORDER_RADIUS,
    COMBO_BORDER_WIDTH,
    COMBO_MIN_HEIGHT,
    COMBO_MIN_WIDTH,
    COMBO_PADDING_X,
    COMBO_PADDING_Y,
    CONTROL_MIN_HEIGHT,
    CONTROL_MIN_WIDTH,
    DIALOG_TITLE_ERROR,
    DIALOG_TITLE_INFO,
    DIALOG_TITLE_SAVE_OK,
    DEFAULT_ALIGNMENT_MODE,
    ERROR_WARNING_THRESHOLD_PX,
    FILE_SELECT_EXPORT_FOLDER_TITLE,
    FILE_SELECT_PHOTO_TITLE,
    FILE_SELECT_PLAN_TITLE,
    FILE_SELECT_PROJECT_LOAD_TITLE,
    FILE_SELECT_PROJECT_SAVE_TITLE,
    FLATTEN_PRESET_DEFAULT,
    FLATTEN_PRESET_INTENSITY_DEFAULT,
    FLATTEN_PRESET_INTENSITY_MAX,
    FLATTEN_PRESET_INTENSITY_MIN,
    FLATTEN_PRESET_KEYS,
    FLATTEN_PRESET_RECORD,
    FLATTEN_PRESET_SHADOW,
    FLATTEN_PRESET_SOFT,
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
    GUIDE_HIDE_TEXT,
    GUIDE_SHOW_TEXT,
    IMAGE_FILE_FILTER,
    IMAGE_PANEL_EMPTY_TEXT,
    IMAGE_PANEL_HEADER_PADDING,
    IMAGE_PANEL_HINT_TEXT,
    IMAGE_PANEL_HINT_TEXT_RGB,
    IMAGE_PANEL_INFO_PADDING,
    IMAGE_PANEL_TEXT_RGB,
    IMAGE_PANEL_TITLE_X,
    INTRO_TITLE,
    INFO_NO_FILE,
    LABEL_FLATTEN_INTENSITY,
    LABEL_FLATTEN_PRESET,
    LABEL_FLATTEN_SPLIT,
    LABEL_OVERLAY_ALPHA,
    LABEL_PHOTO_PANEL,
    LABEL_RESULT_PANEL,
    LABEL_RESULT_VIEW_PREFIX,
    LABEL_RESULT_VIEW_NO_ALIGNMENT,
    LABEL_RESULT_VIEW_NO_PHOTO,
    LABEL_STATUS_PANEL,
    LABEL_VIEW_MODE,
    MIN_ALIGNMENT_POINTS,
    MIN_PANEL_SIZE,
    MSG_ALIGNMENT_COMPLETE_WITH_MODE_FMT,
    MSG_ALIGNMENT_ERROR_FMT,
    MSG_ALIGNMENT_RESULT_INVALID,
    MSG_ALIGNMENT_MODE_CHANGED,
    MSG_ALIGNMENT_MODE_UNSUPPORTED,
    MSG_ALIGNMENT_POSTPROC_ERROR_FMT,
    MSG_ALIGNMENT_CONSTRAINT_FAILED,
    MSG_ALIGNMENT_REQUIRE_POINTS_FMT,
    MSG_ALIGNMENT_TOOLTIP_FMT,
    MSG_ALIGNMENT_READY_TO_ALIGN_FMT,
    MSG_FLATTEN_APPLIED,
    MSG_FILE_LOADED_FMT,
    MSG_FLATTEN_CALC_FAIL_FMT,
    MSG_FLATTEN_PRESET_APPLIED_FMT,
    MSG_FLATTEN_PRESET_INVALID,
    MSG_FLATTEN_REQUIRED,
    MSG_FLATTEN_REQUIRED,
    MSG_LOAD_MISSING_PLAN,
    MSG_LOAD_MISSING_PHOTO,
    MSG_LOAD_PHOTO_ERROR_FMT,
    MSG_LOAD_PLAN_ERROR_FMT,
    MSG_OVERLAY_BASE_MISSING,
    MSG_OVERLAY_IMAGE_MISSING,
    MSG_OVERLAY_PLAN_MISSING,
    MSG_POINT_ADDED_FMT,
    MSG_POINT_MODE_OFF,
    MSG_POINT_MODE_ON,
    MSG_POINT_ORDER_CHANGED,
    MSG_POINT_UNDO_DONE,
    MSG_POINT_REDO_DONE,
    MSG_POINT_HISTORY_EMPTY,
    MSG_POINT_HISTORY_REDO_EMPTY,
    MSG_PNG_SAVE_FAIL_FMT,
    MSG_PROJECT_LOAD_FAIL_FMT,
    MSG_PROJECT_MISSING_PATH_FMT,
    MSG_PROJECT_SAVED_DIALOG_FMT,
    MSG_PROJECT_SAVED_FMT,
    MSG_PROJECT_LOADED_FMT,
    MSG_REQUIRES_PHOTO_FOR_FLAT_COMPARE,
    MSG_QUALITY_GRADE_FMT,
    MSG_QUALITY_NO_ALIGNMENT,
    MSG_QUALITY_OUTLIER_HINT_FMT,
    MSG_QUALITY_RECOMMEND_OUTLIER,
    MSG_QUALITY_SUMMARY_FMT,
    MSG_RESULT_VIEW_FMT,
    MSG_RESULT_VIEW_NO_ALIGNMENT_FMT,
    MSG_RESULT_VIEW_NO_PHOTO_FMT,
    MSG_SELECTED_PHOTO_POINT_DELETED,
    MSG_SELECTED_PLAN_POINT_DELETED,
    MSG_SELECT_POINT_TO_DELETE,
    MSG_EXPORT_ERROR_FMT,
    MSG_EXPORT_MISSING_OVERLAY,
    MSG_EXPORT_MISSING_PLAN,
    MSG_EXPORT_MISSING_PREFIX,
    MSG_EXPORT_NO_IMAGE,
    MSG_EXPORT_REQUIRE_PHOTO,
    MSG_EXPORT_RESULT_MESSAGE,
    MSG_EXPORT_SAVED_FLAT_FMT,
    MSG_EXPORT_SAVED_OVERLAY_FMT,
    MSG_EXPORT_SAVED_WARPED_FMT,
    MSG_EXPORT_SUCCESS_FMT,
    MSG_FLATTEN_PRESET_APPLIED_FMT,
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
    SPLIT_VIEW_DEFAULT_RATIO,
    SPLIT_VIEW_MAX_RATIO,
    SPLIT_VIEW_MIN_RATIO,
    STATUS_FILES_PREFIX,
    STATUS_FILES_SEPARATOR,
    STATUS_GUIDE_PREFIX,
    STATUS_MISMATCH_WARNING,
    STATUS_POINTS_PREFIX,
    STATUS_POINTS_SUFFIX,
    STATUS_POINTS_SEPARATOR,
    STATUS_QUALITY_PREFIX,
    STATUS_QUALITY_RECOMMENDATION,
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
    WORKFLOW_MODE_PHOTO,
    WORKFLOW_MODE_PLAN,
    WORKFLOW_SECTION_SPACING,
    WORKFLOW_STEP_1_LOAD_PHOTO,
    WORKFLOW_STEP_1_LOAD_PLAN,
    WORKFLOW_STEP_ALIGNMENT_DONE,
    WORKFLOW_STEP_ALIGNMENT_MISMATCH_WARN,
    WORKFLOW_STEP_ALIGNMENT_READY,
    WORKFLOW_STEP_FLATTEN_READY,
    WORKFLOW_STEP_POINTS,
    WORKFLOW_STEP_EXPORT_READY,
    WORKFLOW_POINT_EXCLUDE_HELP,
    WORKFLOW_ROW3_SPACING,
    WORKFLOW_ROW_SPACING,
    WORKFLOW_STEP_ALIGNMENT_DONE,
    WORKFLOW_STEP_FLATTEN_READY,
    WORKFLOW_STEP_EXPORT_READY,
    WORKFLOW_STEP_POINTS,
    VIEW_BUTTON_ALIGN,
    VIEW_BUTTON_ALIGN_WITH_SELECTED_EXCLUDED,
    VIEW_BUTTON_EXPORT,
    VIEW_BUTTON_FLATTEN,
    VIEW_BUTTON_LOAD_PROJECT,
    VIEW_BUTTON_OPEN_PLAN,
    VIEW_BUTTON_OPEN_PHOTO,
    VIEW_BUTTON_REMOVE_POINT,
    VIEW_BUTTON_SAVE_PROJECT,
    VIEW_BUTTON_START_POINTS,
    VIEW_MODE_OVERLAY,
    VIEW_MODE_PLAN,
    VIEW_MODE_PHOTO,
    VIEW_TOGGLE_COMPARE_FLAT,
    VIEW_TOGGLE_COMPARE_SPLIT,
    WORKFLOW_STEP_1_LOAD_PHOTO,
    WORKFLOW_STEP_1_LOAD_PLAN,
    WORKFLOW_STEP_POINTS,
    WORKFLOW_STEP_ALIGNMENT_READY,
    WORKFLOW_STEP_ALIGNMENT_DONE,
    VIEW_BUTTON_FLATTEN,
    JSON_CHARSET_ENCODING,
    PALETTE,
    MSG_FLATTEN_CALC_FAIL_FMT,
    VIEW_LABEL_PHOTO,
    VIEW_LABEL_PLAN,
    STATUS_STEP_ALIGNMENT,
    MSG_ALIGNMENT_MODE_CHANGED,
)
from archphotolab.core.export import (
    export_paths,
    now_timestamp,
    save_png,
)
from archphotolab.core.geometry import warp_plan_to_photo
from archphotolab.core.imagery import (
    blend_overlay,
    flatten_illumination,
    load_rgb_image,
    make_split_compare_image,
)
from archphotolab.core.project_io import (
    apply_project_dict_to_state,
    load_project,
    PROJECT_FORMAT,
    ProjectKeys,
    state_to_dict,
    migrate_project_payload,
    resolve_saved_image_path,
)
from archphotolab.state import AppState
from archphotolab.ui.point_editor import PointEditorPanel
from archphotolab.ui.panels import ImagePanel
from archphotolab.ui.status_panel import StatusPanel
from archphotolab.ui.workflow_controller import WorkflowController


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)

        self.state = AppState()
        self.controller = WorkflowController(self.state)
        self.last_dir = str(Path.home())
        self._status_message = ""
        self._point_dragging_side: Optional[str] = None

        self._build_ui()
        self._apply_theme()
        self._set_intro_text(WORKFLOW_INTRO_TEXT)
        self._refresh_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(ROOT_LAYOUT_MARGIN, ROOT_LAYOUT_MARGIN, ROOT_LAYOUT_MARGIN, ROOT_LAYOUT_MARGIN)
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
        self.btn_align_skip = QPushButton(VIEW_BUTTON_ALIGN_WITH_SELECTED_EXCLUDED)
        self.btn_align_skip.clicked.connect(self._run_alignment_excluding_selected_point)
        self.btn_flatten = QPushButton(VIEW_BUTTON_FLATTEN)
        self.btn_flatten.clicked.connect(self._apply_flatten)
        self.chk_compare_flat = QCheckBox(VIEW_TOGGLE_COMPARE_FLAT)
        self.chk_compare_flat.toggled.connect(self._toggle_flat_compare)
        self.chk_compare_split = QCheckBox(VIEW_TOGGLE_COMPARE_SPLIT)
        self.chk_compare_split.toggled.connect(self._toggle_split_compare)
        self.btn_delete_point = QPushButton(VIEW_BUTTON_REMOVE_POINT)
        self.btn_delete_point.clicked.connect(self._clear_selected_point)

        self.point_editor = PointEditorPanel()
        self.point_editor.btn_undo.clicked.connect(self._undo_point)
        self.point_editor.btn_redo.clicked.connect(self._redo_point)
        self.point_editor.btn_up.clicked.connect(lambda: self._reorder_point(-1))
        self.point_editor.btn_down.clicked.connect(lambda: self._reorder_point(1))

        row2.addWidget(self.btn_point_mode)
        row2.addWidget(self.btn_align)
        row2.addWidget(self.btn_align_skip)
        row2.addWidget(self.btn_flatten)
        row2.addWidget(self.chk_compare_flat)
        row2.addWidget(self.chk_compare_split)
        row2.addWidget(self.btn_delete_point)
        row2.addWidget(self.point_editor)
        row2.addWidget(self.btn_export := QPushButton(VIEW_BUTTON_EXPORT))
        row2.addStretch()
        self.btn_export.clicked.connect(self._export_pngs)

        row3 = QHBoxLayout()
        row3.setSpacing(WORKFLOW_ROW_SPACING)
        row3.addWidget(QLabel(LABEL_VIEW_MODE))
        self.cmb_view = QComboBox()
        self.cmb_view.addItem(WORKFLOW_MODE_PHOTO, VIEW_MODE_PHOTO)
        self.cmb_view.addItem(WORKFLOW_MODE_PLAN, VIEW_MODE_PLAN)
        self.cmb_view.addItem(WORKFLOW_MODE_OVERLAY, VIEW_MODE_OVERLAY)
        self.cmb_view.currentIndexChanged.connect(self._on_view_mode_changed)
        row3.addWidget(self.cmb_view)

        row3.addWidget(QLabel(LABEL_OVERLAY_ALPHA))
        self.slider_alpha = QSlider(Qt.Horizontal)
        self.slider_alpha.setRange(0, 100)
        self.slider_alpha.setValue(int(self.state.overlay_alpha * ALPHA_PERCENT_SCALE))
        self.slider_alpha.valueChanged.connect(self._on_alpha_changed)
        self.lbl_alpha = QLabel(f"{int(self.state.overlay_alpha * ALPHA_PERCENT_SCALE)}%")
        self.slider_alpha.setMinimumWidth(SLIDER_MIN_WIDTH)
        self.cmb_view.setMinimumWidth(COMBO_MIN_WIDTH)
        row3.addWidget(self.slider_alpha)
        row3.addWidget(self.lbl_alpha)
        row3.addWidget(QLabel(ALIGNMENT_MODE_LABELS[ALIGNMENT_MODE_HOMOGRAPHY]))
        self.cmb_alignment_mode = QComboBox()
        self.cmb_alignment_mode.addItem(ALIGNMENT_MODE_LABELS[ALIGNMENT_MODE_HOMOGRAPHY], ALIGNMENT_MODE_HOMOGRAPHY)
        self.cmb_alignment_mode.addItem(ALIGNMENT_MODE_LABELS[ALIGNMENT_MODE_AFFINE], ALIGNMENT_MODE_AFFINE)
        self.cmb_alignment_mode.addItem(ALIGNMENT_MODE_LABELS[ALIGNMENT_MODE_SIMILARITY], ALIGNMENT_MODE_SIMILARITY)
        self.cmb_alignment_mode.currentIndexChanged.connect(self._on_alignment_mode_changed)
        row3.addWidget(self.cmb_alignment_mode)
        row3.addStretch()

        row4 = QHBoxLayout()
        row4.setSpacing(WORKFLOW_ROW3_SPACING)
        row4.addWidget(QLabel(LABEL_FLATTEN_PRESET))
        self.cmb_flatten_preset = QComboBox()
        self.cmb_flatten_preset.addItem(FLATTEN_PRESET_RECORD, FLATTEN_PRESET_RECORD)
        self.cmb_flatten_preset.addItem(FLATTEN_PRESET_SHADOW, FLATTEN_PRESET_SHADOW)
        self.cmb_flatten_preset.addItem(FLATTEN_PRESET_SOFT, FLATTEN_PRESET_SOFT)
        self.cmb_flatten_preset.currentIndexChanged.connect(self._on_flatten_preset_changed)
        self.cmb_flatten_preset.setCurrentText(self.state.flatten_preset)
        row4.addWidget(self.cmb_flatten_preset)
        row4.addWidget(QLabel(LABEL_FLATTEN_INTENSITY))
        self.slider_flat_intensity = QSlider(Qt.Horizontal)
        self.slider_flat_intensity.setRange(FLATTEN_PRESET_INTENSITY_MIN, FLATTEN_PRESET_INTENSITY_MAX)
        self.slider_flat_intensity.setValue(self.state.flatten_intensity)
        self.slider_flat_intensity.valueChanged.connect(self._on_flatten_intensity_changed)
        self.lbl_flat_intensity = QLabel(f"{self.state.flatten_intensity}%")
        self.slider_flat_intensity.setMinimumWidth(SLIDER_MIN_WIDTH)
        row4.addWidget(self.slider_flat_intensity)
        row4.addWidget(self.lbl_flat_intensity)
        row4.addWidget(QLabel(LABEL_FLATTEN_SPLIT))
        self.slider_split_ratio = QSlider(Qt.Horizontal)
        self.slider_split_ratio.setRange(5, 95)
        self.slider_split_ratio.setValue(int(self.state.split_ratio * 100))
        self.slider_split_ratio.valueChanged.connect(self._on_split_ratio_changed)
        self.lbl_split_ratio = QLabel(f"{int(self.state.split_ratio * 100)}%")
        self.slider_split_ratio.setMinimumWidth(SLIDER_MIN_WIDTH)
        row4.addWidget(self.slider_split_ratio)
        row4.addWidget(self.lbl_split_ratio)
        row4.addStretch()

        controls.addLayout(row1)
        controls.addLayout(row2)
        controls.addLayout(row3)
        controls.addLayout(row4)

        panels = QHBoxLayout()
        self.photo_panel, self.photo_view, self.photo_info = self._create_panel(LABEL_PHOTO_PANEL)
        self.plan_panel, self.plan_view, self.plan_info = self._create_panel(LABEL_PLAN_PANEL)
        self.result_panel, self.result_view, self.result_info = self._create_panel(LABEL_RESULT_PANEL, editable=False)
        self.photo_panel.setObjectName(QOBJECT_WORK_PANEL)
        self.plan_panel.setObjectName(QOBJECT_WORK_PANEL)
        self.result_panel.setObjectName(QOBJECT_WORK_PANEL)

        panels.addWidget(self.photo_panel, 1)
        panels.addWidget(self.plan_panel, 1)
        panels.addWidget(self.result_panel, 1)

        self.status_panel = StatusPanel()
        self.status_panel.setObjectName(QOBJECT_STATUS_PANEL)

        self.photo_view.pointAdded.connect(lambda x, y: self._on_point_added(VIEW_MODE_PHOTO, x, y))
        self.plan_view.pointAdded.connect(lambda x, y: self._on_point_added(VIEW_MODE_PLAN, x, y))
        self.photo_view.pointMoveStarted.connect(lambda i, x, y: self._on_point_move_started(VIEW_MODE_PHOTO, i, x, y))
        self.plan_view.pointMoveStarted.connect(lambda i, x, y: self._on_point_move_started(VIEW_MODE_PLAN, i, x, y))
        self.photo_view.pointMoved.connect(lambda i, x, y: self._on_point_moved(VIEW_MODE_PHOTO, i, x, y))
        self.plan_view.pointMoved.connect(lambda i, x, y: self._on_point_moved(VIEW_MODE_PLAN, i, x, y))
        self.photo_view.pointMoveFinished.connect(lambda i, x, y: self._on_point_move_finished(VIEW_MODE_PHOTO, i, x, y))
        self.plan_view.pointMoveFinished.connect(lambda i, x, y: self._on_point_move_finished(VIEW_MODE_PLAN, i, x, y))
        self.photo_view.pointRemoved.connect(lambda i: self._on_point_removed(VIEW_MODE_PHOTO, i))
        self.plan_view.pointRemoved.connect(lambda i: self._on_point_removed(VIEW_MODE_PLAN, i))
        self.photo_view.pointSelected.connect(lambda i: self._on_point_selected(VIEW_MODE_PHOTO, i))
        self.plan_view.pointSelected.connect(lambda i: self._on_point_selected(VIEW_MODE_PLAN, i))
        self.photo_view.viewStateChanged.connect(
            lambda zoom, pan_x, pan_y: self._on_view_state_changed(VIEW_MODE_PHOTO, zoom, pan_x, pan_y),
        )
        self.plan_view.viewStateChanged.connect(
            lambda zoom, pan_x, pan_y: self._on_view_state_changed(VIEW_MODE_PLAN, zoom, pan_x, pan_y),
        )

        controls_widget = QWidget()
        controls_widget.setLayout(controls)

        root_layout.addWidget(intro_box)
        root_layout.addWidget(controls_widget)
        root_layout.addLayout(panels, stretch=8)
        root_layout.addWidget(self.status_panel)

        self._apply_control_style(
            self.btn_open_photo,
            self.btn_open_plan,
            self.btn_load_project,
            self.btn_save_project,
            self.btn_point_mode,
            self.btn_align,
            self.btn_flatten,
            self.btn_align_skip,
            self.btn_delete_point,
            self.btn_export,
            self.point_editor.btn_undo,
            self.point_editor.btn_redo,
            self.point_editor.btn_up,
            self.point_editor.btn_down,
            self.btn_compare_checkbox(),
        )

    def btn_compare_checkbox(self) -> QCheckBox:
        return self.chk_compare_flat

    def _apply_control_style(self, *widgets: object) -> None:
        for widget in widgets:
            if isinstance(widget, (QPushButton, QComboBox, QCheckBox, QSlider)):
                widget.setMinimumHeight(CONTROL_MIN_HEIGHT)
                widget.setMinimumWidth(CONTROL_MIN_WIDTH)

    def _apply_theme(self) -> None:
        pal = PALETTE
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
        self.lbl_intro.setVisible(checked)
        self.btn_toggle_intro.setText(GUIDE_HIDE_TEXT if checked else GUIDE_SHOW_TEXT)

    def _set_intro_text(self, text: str) -> None:
        self.lbl_intro.setText(text)

    def _create_panel(self, title: str, editable: bool = True):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QLabel(title)
        header_font = QFont()
        header_font.setPointSize(UI_TITLE_FONT_SIZE)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet(f"padding: {IMAGE_PANEL_HEADER_PADDING}; color: #e6edf7;")

        view = ImagePanel(title=title, editable=editable)
        view.setMinimumSize(*MIN_PANEL_SIZE)
        info = QLabel(IMAGE_PANEL_EMPTY_TEXT)
        info.setWordWrap(True)
        info.setStyleSheet(f"padding: {IMAGE_PANEL_INFO_PADDING}; color: #96a9c1;")

        layout.addWidget(header)
        layout.addWidget(view, stretch=1)
        layout.addWidget(info)
        return container, view, info

    def _on_alignment_mode_changed(self) -> None:
        mode = str(self.cmb_alignment_mode.currentData())
        try:
            self.controller.set_alignment_mode(mode)
            self._set_message(MSG_ALIGNMENT_MODE_CHANGED)
        except ValueError:
            self._set_message(MSG_ALIGNMENT_MODE_UNSUPPORTED, is_error=True)
            self.cmb_alignment_mode.setCurrentText(ALIGNMENT_MODE_LABELS[DEFAULT_ALIGNMENT_MODE])

    def _on_split_ratio_changed(self, value: int) -> None:
        ratio = max(SPLIT_VIEW_MIN_RATIO, min(SPLIT_VIEW_MAX_RATIO, value / 100.0))
        self.state.split_ratio = ratio
        self.lbl_split_ratio.setText(f"{int(ratio * 100)}%")
        self._refresh_ui()

    def _on_flatten_intensity_changed(self, value: int) -> None:
        self.state.flatten_intensity = int(value)
        self.lbl_flat_intensity.setText(f"{value}%")
        if self.state.show_flat_photo:
            self._recompute_flattened_photo(force=True)
            self._set_message(MSG_FLATTEN_PRESET_APPLIED_FMT.format(preset=self.state.flatten_preset, intensity=value))
        self._refresh_ui()

    def _on_flatten_preset_changed(self) -> None:
        preset = str(self.cmb_flatten_preset.currentData())
        if preset not in FLATTEN_PRESET_KEYS:
            self._set_message(MSG_FLATTEN_PRESET_INVALID, is_error=True)
            self.cmb_flatten_preset.setCurrentText(self.state.flatten_preset)
            return

        if self.state.flatten_preset == preset:
            return

        self.state.flatten_preset = preset
        if self.state.show_flat_photo:
            self._recompute_flattened_photo(force=True)
            self._set_message(MSG_FLATTEN_PRESET_APPLIED_FMT.format(preset=preset, intensity=self.state.flatten_intensity))
        self._refresh_ui()

    def _toggle_point_mode(self, enabled: bool) -> None:
        self.photo_view.set_editable(enabled)
        self.plan_view.set_editable(enabled)
        self._set_message(MSG_POINT_MODE_ON if enabled else MSG_POINT_MODE_OFF)

    def _on_view_state_changed(self, side: str, zoom: float, pan_x: int, pan_y: int) -> None:
        if side == VIEW_MODE_PHOTO:
            self.state.photo_view_zoom = float(zoom)
            self.state.photo_view_pan_x = int(pan_x)
            self.state.photo_view_pan_y = int(pan_y)
            return
        if side == VIEW_MODE_PLAN:
            self.state.plan_view_zoom = float(zoom)
            self.state.plan_view_pan_x = int(pan_x)
            self.state.plan_view_pan_y = int(pan_y)

    def _on_view_mode_changed(self) -> None:
        self.state.result_view_mode = str(self.cmb_view.currentData())
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
                self._recompute_flattened_photo(force=True)
            self.state.show_flat_photo = True
        else:
            self.state.show_flat_photo = False
            self.chk_compare_split.setChecked(False)
            self.state.show_split_compare = False
        self._refresh_ui()

    def _toggle_split_compare(self, checked: bool) -> None:
        if checked and self.state.flattened_photo is None:
            if self.state.photo_image is None:
                self.chk_compare_split.setChecked(False)
                self._set_message(MSG_REQUIRES_PHOTO_FOR_FLAT_COMPARE, is_error=True)
                return
            self._recompute_flattened_photo(force=True)
        self.state.show_split_compare = bool(checked)
        self._refresh_ui()

    def _ensure_flattened(self, force: bool = False) -> Optional[np.ndarray]:
        if self.state.photo_image is None:
            return None
        if self.state.flattened_photo is not None and not force:
            return self.state.flattened_photo
        self.state.flattened_photo = flatten_illumination(
            self.state.photo_image,
            preset=self.state.flatten_preset,
            intensity=self.state.flatten_intensity,
        )
        return self.state.flattened_photo

    def _recompute_flattened_photo(self, force: bool = False) -> None:
        image = self.state.photo_image
        if image is None:
            return
        self.state.flattened_photo = flatten_illumination(
            image,
            preset=self.state.flatten_preset,
            intensity=self.state.flatten_intensity,
        )
        self.state.show_flat_photo = True

    def _photo_view_display_image(self) -> Optional[np.ndarray]:
        if self.state.photo_image is None:
            return None
        if not self.state.show_flat_photo or self.state.flattened_photo is None:
            return self.state.photo_image
        if self.state.show_split_compare and self.state.split_ratio > 0:
            return make_split_compare_image(
                self.state.photo_image,
                self.state.flattened_photo,
                ratio=self.state.split_ratio,
            )
        return self.state.flattened_photo

    def _photo_result_base_image(self) -> Optional[np.ndarray]:
        if self.state.photo_image is None:
            return None
        if self.state.show_flat_photo and self.state.flattened_photo is not None:
            return self.state.flattened_photo
        return self.state.photo_image

    def _on_point_added(self, side: str, x: float, y: float) -> None:
        if not self.btn_point_mode.isChecked():
            return

        image = self.state.photo_image if side == VIEW_MODE_PHOTO else self.state.plan_image
        if image is None:
            return
        self.controller.add_point(
            side=side,
            x=x,
            y=y,
            image_width=image.shape[1],
            image_height=image.shape[0],
        )
        side_label = VIEW_LABEL_PHOTO if side == VIEW_MODE_PHOTO else VIEW_LABEL_PLAN
        count = len(self.state.photo_points) if side == VIEW_MODE_PHOTO else len(self.state.plan_points)
        self._set_message(MSG_POINT_ADDED_FMT.format(side=side_label, count=count))
        self._refresh_ui()

    def _on_point_move_started(self, side: str, index: int, x: float, y: float) -> None:
        if not self.btn_point_mode.isChecked():
            return
        image = self.state.photo_image if side == VIEW_MODE_PHOTO else self.state.plan_image
        if image is None:
            return
        self._point_dragging_side = side
        self.controller.move_point(
            side=side,
            index=index,
            x=x,
            y=y,
            image_width=image.shape[1],
            image_height=image.shape[0],
            record_history=False,
        )
        self._refresh_point_overlays()

    def _on_point_moved(self, side: str, index: int, x: float, y: float) -> None:
        if not self.btn_point_mode.isChecked():
            return
        image = self.state.photo_image if side == VIEW_MODE_PHOTO else self.state.plan_image
        if image is None:
            return
        self.controller.move_point(
            side=side,
            index=index,
            x=x,
            y=y,
            image_width=image.shape[1],
            image_height=image.shape[0],
            record_history=False,
        )
        self._refresh_point_overlays()

    def _on_point_move_finished(self, side: str, index: int, x: float, y: float) -> None:
        image = self.state.photo_image if side == VIEW_MODE_PHOTO else self.state.plan_image
        if image is None or not self.btn_point_mode.isChecked():
            return
        self.controller.move_point(
            side=side,
            index=index,
            x=x,
            y=y,
            image_width=image.shape[1],
            image_height=image.shape[0],
            record_history=True,
        )
        self._point_dragging_side = None
        self._refresh_ui()

    def _on_point_moved_simple(self, side: str, index: int, x: float, y: float) -> None:
        image = self.state.photo_image if side == VIEW_MODE_PHOTO else self.state.plan_image
        if image is None:
            return
        self.controller.move_point(
            side=side,
            index=index,
            x=x,
            y=y,
            image_width=image.shape[1],
            image_height=image.shape[0],
            record_history=False,
        )

    def _on_point_selected(self, side: str, index: int) -> None:
        self.controller.select_point(side, index)
        self._refresh_point_overlays()

    def _on_point_removed(self, side: str, index: int) -> None:
        if not self.btn_point_mode.isChecked():
            return
        self.controller.remove_point(side, index)
        self._refresh_ui()

    def _clear_selected_point(self) -> None:
        if self.state.selected_photo_point is not None:
            self._on_point_removed(VIEW_MODE_PHOTO, self.state.selected_photo_point)
            self._set_message(MSG_SELECTED_PHOTO_POINT_DELETED)
            return
        if self.state.selected_plan_point is not None:
            self._on_point_removed(VIEW_MODE_PLAN, self.state.selected_plan_point)
            self._set_message(MSG_SELECTED_PLAN_POINT_DELETED)
            return
        self._set_message(MSG_SELECT_POINT_TO_DELETE, is_error=True)

    def _undo_point(self) -> None:
        try:
            self.controller.undo_point()
            self._refresh_ui()
            self._set_message(MSG_POINT_UNDO_DONE)
        except RuntimeError as exc:
            self._set_message(str(exc), is_error=True)

    def _redo_point(self) -> None:
        try:
            self.controller.redo_point()
            self._refresh_ui()
            self._set_message(MSG_POINT_REDO_DONE)
        except RuntimeError as exc:
            self._set_message(str(exc), is_error=True)

    def _reorder_point(self, direction: int) -> None:
        side = self.state.selected_point_side
        if side not in (VIEW_MODE_PHOTO, VIEW_MODE_PLAN):
            return
        self.controller.reorder_point(side, direction)
        self._set_message(MSG_POINT_ORDER_CHANGED)
        self._refresh_ui()

    def _apply_flatten(self) -> None:
        if self.state.photo_image is None:
            self._set_message(MSG_FLATTEN_REQUIRED, is_error=True)
            return
        try:
            self._recompute_flattened_photo(force=True)
            self.chk_compare_flat.setChecked(True)
            self._set_message(MSG_FLATTEN_APPLIED)
            self._refresh_ui()
        except Exception as exc:
            self._set_message(MSG_FLATTEN_CALC_FAIL_FMT.format(error=exc), is_error=True)

    def _compose_overlay(self) -> np.ndarray:
        base = self._photo_result_base_image()
        if base is None:
            raise ValueError(MSG_OVERLAY_BASE_MISSING)
        if self.state.warped_plan is None:
            raise ValueError(MSG_OVERLAY_PLAN_MISSING)
        if base.shape[:2] != self.state.warped_plan.shape[:2]:
            raise ValueError(MSG_OVERLAY_IMAGE_SIZE_MISMATCH)
        return blend_overlay(base, self.state.warped_plan, self.state.overlay_alpha)

    def _run_alignment(self) -> None:
        success, result, error = self.controller.run_alignment()
        self._handle_alignment_result(success, result, error, "정합 완료")

    def _run_alignment_excluding_selected_point(self) -> None:
        success, result, error = self.controller.run_alignment_excluding_selected_pair()
        self._handle_alignment_result(success, result, error, "선택점 제외 정합 완료")

    def _handle_alignment_result(
        self,
        success: bool,
        result,
        error: Optional[str],
        fallback_message: str,
    ) -> None:
        if not success:
            fallback = MSG_ALIGNMENT_ERROR_FMT.format(error=MSG_ALIGNMENT_CONSTRAINT_FAILED)
            self._set_message(error or fallback, is_error=True)
            if error is None:
                self._set_message(fallback, is_error=True)
            self._refresh_ui()
            return

        if result.matrix is None:
            self._set_message(
                MSG_ALIGNMENT_POSTPROC_ERROR_FMT.format(error=result.error_message or MSG_ALIGNMENT_RESULT_INVALID),
                is_error=True,
            )
            self._refresh_ui()
            return

        if self.state.warped_plan is None:
            self._set_message(MSG_ALIGNMENT_POSTPROC_ERROR_FMT.format(error=MSG_ALIGNMENT_RESULT_INVALID), is_error=True)
            self._refresh_ui()
            return

        self.state.result_view_mode = VIEW_MODE_OVERLAY
        self._set_combo_by_value(self.state.result_view_mode)
        self._set_combo_by_value(self.state.alignment_mode, is_alignment=True)
        quality = self.state.quality_profile
        self._set_message(
            MSG_ALIGNMENT_COMPLETE_WITH_MODE_FMT.format(
                mode=ALIGNMENT_MODE_LABELS.get(self.state.alignment_mode, fallback_message),
                avg=quality.average_error or 0.0,
                median=quality.median_error or 0.0,
                max=quality.max_error or 0.0,
            )
        )
        self._refresh_ui()

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
            saved = []
            missing = []

            flat_image = self.state.flattened_photo
            if flat_image is None and self.state.photo_image is not None:
                flat_image = self._ensure_flattened(force=True)
            if flat_image is None:
                raise ValueError(MSG_FLATTEN_REQUIRED)
            save_png(flat_path, flat_image)
            saved.append(MSG_EXPORT_SAVED_FLAT_FMT.format(filename=Path(flat_path).name))

            if self.state.warped_plan is not None:
                save_png(warped_path, self.state.warped_plan)
                saved.append(MSG_EXPORT_SAVED_WARPED_FMT.format(filename=Path(warped_path).name))
                save_png(overlay_path, self._compose_overlay())
                saved.append(MSG_EXPORT_SAVED_OVERLAY_FMT.format(filename=Path(overlay_path).name))
            else:
                missing.append(MSG_EXPORT_MISSING_OVERLAY)
                missing.append(MSG_EXPORT_MISSING_PLAN)

            message = "\n".join(saved)
            if missing:
                message += f"\n\n{MSG_EXPORT_MISSING_PREFIX}{', '.join(missing)}"
            QMessageBox.information(
                self,
                DIALOG_TITLE_SAVE_OK,
                MSG_EXPORT_RESULT_MESSAGE.format(message=message, path=output_dir),
            )
            self._set_message(MSG_EXPORT_SUCCESS_FMT.format(path=output_dir))
        except Exception as exc:
            self._set_message(MSG_EXPORT_ERROR_FMT.format(error=exc), is_error=True)
            QMessageBox.warning(self, DIALOG_TITLE_ERROR, MSG_PNG_SAVE_FAIL_FMT.format(error=exc))

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
        payload[ProjectKeys.FORMAT_VERSION] = PROJECT_FORMAT

        with open(file_path, "w", encoding=JSON_CHARSET_ENCODING) as f:
            import json

            json.dump(payload, f, ensure_ascii=False, indent=2)

        self.state.last_project_file = file_path
        self._set_message(MSG_PROJECT_SAVED_FMT.format(path=file_path))
        QMessageBox.information(self, DIALOG_TITLE_INFO, MSG_PROJECT_SAVED_DIALOG_FMT.format(path=file_path))
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
            loaded_raw = load_project(file_path)
            loaded_payload, migration_warnings = migrate_project_payload(loaded_raw)
            self.state = apply_project_dict_to_state(loaded_payload)
            self.controller = WorkflowController(self.state)

            missing: list[str] = []
            if self.state.photo_path:
                resolved = resolve_saved_image_path(self.state.photo_path, file_path, [self.last_dir])
                if resolved:
                    self.state.photo_path = resolved
                    self.state.photo_image = load_rgb_image(resolved)
                else:
                    self.state.photo_image = None
                    self.state.photo_points = []
                    missing.append(MSG_LOAD_MISSING_PHOTO)

            if self.state.plan_path:
                resolved = resolve_saved_image_path(self.state.plan_path, file_path, [self.last_dir])
                if resolved:
                    self.state.plan_path = resolved
                    self.state.plan_image = load_rgb_image(resolved)
                else:
                    self.state.plan_image = None
                    self.state.plan_points = []
                    missing.append(MSG_LOAD_MISSING_PLAN)

            if self.state.photo_image is not None and self.state.plan_image is not None:
                if self.state.flatten_preset not in FLATTEN_PRESET_KEYS:
                    self.state.flatten_preset = FLATTEN_PRESET_DEFAULT
                self.state.flatten_intensity = int(self.state.flatten_intensity)
                if self.state.show_flat_photo:
                    self._recompute_flattened_photo(force=True)

                if self.state.homography is not None:
                    try:
                        self.state.warped_plan = warp_plan_to_photo(
                            self.state.plan_image,
                            self.state.homography,
                            self.state.photo_image.shape,
                            mode=self.state.alignment_mode,
                        )
                    except Exception:
                        self.state.clear_alignment()

            self._set_combo_by_value(self.state.result_view_mode)
            self._set_combo_by_value(self.state.alignment_mode, is_alignment=True)
            self._set_combo_by_value(self.state.flatten_preset, is_flatten=True)
            self.slider_flat_intensity.setValue(self.state.flatten_intensity)
            self.slider_alpha.setValue(int(self.state.overlay_alpha * ALPHA_PERCENT_SCALE))
            self.chk_compare_flat.setChecked(self.state.show_flat_photo)
            self.chk_compare_split.setChecked(self.state.show_split_compare)
            self.slider_split_ratio.setValue(int(self.state.split_ratio * 100))
            self.cmb_view.setCurrentText(self._view_mode_label(self.state.result_view_mode))
            self._set_combo_by_value(self.state.alignment_mode, is_alignment=True)
            self.cmb_flatten_preset.setCurrentText(self.state.flatten_preset)

            message = MSG_PROJECT_LOADED_FMT.format(name=Path(file_path).name)
            if migration_warnings:
                message += f"\n{', '.join(migration_warnings)}"
            if missing:
                message += f"\n{MSG_PROJECT_MISSING_PATH_FMT.format(paths=', '.join(missing))}"
            self._set_message(message)
            self.state.last_project_file = file_path
            self._refresh_ui()
        except Exception as exc:
            self._set_message(MSG_PROJECT_LOAD_FAIL_FMT.format(error=exc), is_error=True)
            QMessageBox.warning(self, DIALOG_TITLE_ERROR, MSG_PROJECT_LOAD_FAIL_FMT.format(error=exc))

    def _set_combo_by_value(self, value: str, is_alignment: bool = False, is_flatten: bool = False) -> None:
        if is_alignment:
            combo = self.cmb_alignment_mode
        elif is_flatten:
            combo = self.cmb_flatten_preset
        else:
            combo = self.cmb_view

        for i in range(combo.count()):
            if str(combo.itemData(i)) == value:
                combo.setCurrentIndex(i)
                return
            if combo.itemText(i) == value and is_alignment:
                combo.setCurrentIndex(i)
                return
            if combo.itemText(i) == value and is_flatten:
                combo.setCurrentIndex(i)
                return

    def _view_mode_label(self, mode: str) -> str:
        if mode == VIEW_MODE_PHOTO:
            return WORKFLOW_MODE_PHOTO
        if mode == VIEW_MODE_PLAN:
            return WORKFLOW_MODE_PLAN
        if mode == VIEW_MODE_OVERLAY:
            return WORKFLOW_MODE_OVERLAY
        return WORKFLOW_MODE_OVERLAY

    def _refresh_ui(self) -> None:
        self._sync_controls()
        self._refresh_panel_images()
        self._refresh_point_overlays()
        self._refresh_result_view()
        self._refresh_status()

    def _sync_controls(self) -> None:
        self.photo_view.set_editable(self.btn_point_mode.isChecked())
        self.plan_view.set_editable(self.btn_point_mode.isChecked())
        self.btn_align.setEnabled(
            self.state.photo_image is not None
            and self.state.plan_image is not None
            and len(self.state.photo_points) >= MIN_ALIGNMENT_POINTS
            and len(self.state.plan_points) >= MIN_ALIGNMENT_POINTS
            and len(self.state.photo_points) == len(self.state.plan_points)
        )
        self.btn_align_skip.setEnabled(self.btn_align.isEnabled() and self.controller._selected_pair_index() is not None)
        self.btn_align.setToolTip(
            MSG_ALIGNMENT_TOOLTIP_FMT.format(min_points=MIN_ALIGNMENT_POINTS)
            if not self.btn_align.isEnabled()
            else MSG_ALIGNMENT_READY_TO_ALIGN_FMT
        )
        self.btn_align_skip.setToolTip(
            WORKFLOW_POINT_EXCLUDE_HELP if self.btn_align_skip.isEnabled() else MSG_SELECT_POINT_TO_DELETE
        )
        self.point_editor.btn_undo.setEnabled(len(self.state.point_history) > 1)
        self.point_editor.btn_redo.setEnabled(len(self.state.point_redo) > 0)

        selected_side = self.state.selected_point_side
        selected_index = (
            self.state.selected_photo_point
            if selected_side == VIEW_MODE_PHOTO
            else self.state.selected_plan_point
        )
        points_len = len(self.state.photo_points) if selected_side == VIEW_MODE_PHOTO else len(self.state.plan_points)
        self.point_editor.btn_up.setEnabled(selected_index is not None and selected_index > 0 and points_len >= 2)
        self.point_editor.btn_down.setEnabled(
            selected_index is not None
            and selected_index >= 0
            and selected_index < points_len - 1
            and points_len >= 2
        )

        self.btn_flatten.setEnabled(self.state.photo_image is not None)
        self.slider_alpha.setEnabled(self.state.warped_plan is not None)
        self.btn_export.setEnabled(self.state.photo_image is not None)
        self.btn_delete_point.setEnabled(
            self.state.selected_photo_point is not None or self.state.selected_plan_point is not None,
        )

        self.chk_compare_flat.setEnabled(self.state.photo_image is not None)
        self.cmb_flatten_preset.setEnabled(self.state.photo_image is not None)
        self.slider_flat_intensity.setEnabled(self.state.photo_image is not None)
        self.chk_compare_split.setEnabled(self.state.photo_image is not None)
        self.slider_split_ratio.setEnabled(self.state.photo_image is not None and self.state.flattened_photo is not None)
        self.cmb_alignment_mode.setEnabled(self.state.photo_image is not None and self.state.plan_image is not None)
        self.btn_align.setText(VIEW_BUTTON_ALIGN)

    def _refresh_panel_images(self) -> None:
        photo_info = IMAGE_PANEL_EMPTY_TEXT
        if self.state.photo_image is None:
            self.photo_view.set_image(None)
            photo_info = f"{VIEW_LABEL_PHOTO}: {INFO_NO_FILE}"
        else:
            self.photo_view.set_view_state(
                self.state.photo_view_zoom,
                self.state.photo_view_pan_x,
                self.state.photo_view_pan_y,
            )
            self.photo_view.set_image(self._photo_view_display_image())
            photo_name = Path(self.state.photo_path).name if self.state.photo_path else TEMP_FILE_NAME
            photo_info = f"{VIEW_LABEL_PHOTO}: {photo_name} ({self.state.photo_image.shape[1]} x {self.state.photo_image.shape[0]})"
        self.photo_info.setText(photo_info)

        plan_info = IMAGE_PANEL_EMPTY_TEXT
        if self.state.plan_image is None:
            self.plan_view.set_image(None)
            plan_info = f"{VIEW_LABEL_PLAN}: {INFO_NO_FILE}"
        else:
            self.plan_view.set_view_state(
                self.state.plan_view_zoom,
                self.state.plan_view_pan_x,
                self.state.plan_view_pan_y,
            )
            self.plan_view.set_image(self.state.plan_image)
            plan_name = Path(self.state.plan_path).name if self.state.plan_path else TEMP_FILE_NAME
            plan_info = f"{VIEW_LABEL_PLAN}: {plan_name} ({self.state.plan_image.shape[1]} x {self.state.plan_image.shape[0]})"
        self.plan_info.setText(plan_info)

    def _warning_indices(self) -> set[int]:
        threshold = ERROR_WARNING_THRESHOLD_PX
        warnings: set[int] = set()
        for idx, error in enumerate(self.state.reprojection_errors):
            if error > threshold:
                warnings.add(idx)
        warnings.update(self.state.outlier_indices)
        return warnings

    def _paired_indices(self) -> tuple[Optional[int], Optional[int]]:
        paired_photo = None
        paired_plan = None
        if self.state.selected_point_side == VIEW_MODE_PHOTO and self.state.selected_photo_point is not None:
            paired_plan = self.state.selected_photo_point
        elif self.state.selected_point_side == VIEW_MODE_PLAN and self.state.selected_plan_point is not None:
            paired_photo = self.state.selected_plan_point
        return paired_photo, paired_plan

    def _refresh_point_overlays(self) -> None:
        paired_photo, paired_plan = self._paired_indices()
        warning = self._warning_indices()
        self.photo_view.set_points(
            self.state.photo_points,
            warning_indices=warning,
            selected_index=self.state.selected_photo_point,
            paired_index=paired_photo,
        )
        self.plan_view.set_points(
            self.state.plan_points,
            warning_indices=warning,
            selected_index=self.state.selected_plan_point,
            paired_index=paired_plan,
        )

    def _result_panel_text(self, mode: str) -> str:
        if mode == VIEW_MODE_PHOTO:
            return LABEL_RESULT_VIEW_PREFIX + WORKFLOW_MODE_PHOTO
        if mode == VIEW_MODE_PLAN:
            return LABEL_RESULT_VIEW_PREFIX + WORKFLOW_MODE_PLAN
        return LABEL_RESULT_VIEW_PREFIX + WORKFLOW_MODE_OVERLAY

    def _refresh_result_view(self) -> None:
        mode = self._current_view_mode()
        self.state.result_view_mode = mode

        if mode == VIEW_MODE_PHOTO:
            self.result_view.set_image(self._photo_view_display_image())
            self.result_info.setText(MSG_RESULT_VIEW_FMT.format(mode=WORKFLOW_MODE_PHOTO))
            return

        if mode == VIEW_MODE_PLAN:
            if self.state.plan_image is None:
                self.result_view.set_image(None)
                self.result_info.setText(MSG_RESULT_VIEW_NO_PHOTO_FMT.format(mode=WORKFLOW_MODE_PLAN))
                return
            self.result_view.set_image(self.state.plan_image)
            self.result_info.setText(MSG_RESULT_VIEW_FMT.format(mode=WORKFLOW_MODE_PLAN))
            return

        if self.state.photo_image is None:
            self.result_view.set_image(None)
            self.result_info.setText(MSG_RESULT_VIEW_NO_PHOTO_FMT.format(mode=WORKFLOW_MODE_OVERLAY))
            return

        if self.state.warped_plan is None:
            self.result_view.set_image(self._photo_result_base_image())
            self.result_info.setText(MSG_RESULT_VIEW_NO_ALIGNMENT_FMT.format(mode=WORKFLOW_MODE_OVERLAY))
            return

        self.result_view.set_image(self._compose_overlay())
        self.result_info.setText(MSG_RESULT_VIEW_FMT.format(mode=WORKFLOW_MODE_OVERLAY))

    def _quality_grade_text(self) -> str:
        if self.state.quality_profile.grade:
            return f"{STATUS_QUALITY_PREFIX}{self.state.quality_profile.grade}"
        return MSG_QUALITY_NO_ALIGNMENT

    def _quality_summary(self) -> str:
        if self.state.reprojection_avg is None or self.state.reprojection_median is None or self.state.reprojection_max is None:
            return MSG_QUALITY_NO_ALIGNMENT
        return MSG_QUALITY_SUMMARY_FMT.format(
            avg=self.state.reprojection_avg,
            median=self.state.reprojection_median,
            max=self.state.reprojection_max,
            warn_count=len(self.state.outlier_indices),
        )

    def _refresh_status(self) -> None:
        photo_name = Path(self.state.photo_path).name if self.state.photo_path else INFO_NO_FILE
        plan_name = Path(self.state.plan_path).name if self.state.plan_path else INFO_NO_FILE
        files = f"{STATUS_FILES_PREFIX}{photo_name}{STATUS_FILES_SEPARATOR}{VIEW_LABEL_PLAN}: {plan_name}"
        points = (
            f"{STATUS_POINTS_PREFIX}{len(self.state.photo_points)}"
            f"{STATUS_POINTS_SEPARATOR}{len(self.state.plan_points)}{STATUS_POINTS_SUFFIX}"
        )

        if len(self.state.photo_points) != len(self.state.plan_points):
            mismatch = STATUS_MISMATCH_WARNING
            guide = f"{STATUS_GUIDE_PREFIX}{WORKFLOW_STEP_ALIGNMENT_MISMATCH_WARN}"
        elif self.state.photo_image is None:
            mismatch = ""
            guide = f"{STATUS_GUIDE_PREFIX}{WORKFLOW_STEP_1_LOAD_PHOTO}"
        elif self.state.plan_image is None:
            mismatch = ""
            guide = f"{STATUS_GUIDE_PREFIX}{WORKFLOW_STEP_1_LOAD_PLAN}"
        elif len(self.state.photo_points) < MIN_ALIGNMENT_POINTS:
            guide = f"{STATUS_GUIDE_PREFIX}{WORKFLOW_STEP_POINTS.format(min_points=MIN_ALIGNMENT_POINTS)}"
            mismatch = ""
        elif self.state.homography is None:
            guide = f"{STATUS_GUIDE_PREFIX}{WORKFLOW_STEP_ALIGNMENT_READY}"
            mismatch = ""
        else:
            guide = f"{STATUS_GUIDE_PREFIX}{WORKFLOW_STEP_ALIGNMENT_DONE}"
            mismatch = ""

        if len(self.state.photo_points) < MIN_ALIGNMENT_POINTS and len(self.state.plan_points) < MIN_ALIGNMENT_POINTS:
            step = f"{STATUS_STEP_PREFIX}{STATUS_STEP_POINTS}"
        elif self.state.homography is None:
            step = f"{STATUS_STEP_PREFIX}{STATUS_STEP_ALIGNMENT}"
        else:
            step = f"{STATUS_STEP_PREFIX}{STATUS_STEP_ALIGNMENT_DONE}"

        quality_text = self._quality_summary()
        grade_text = self._quality_grade_text()
        if self.state.quality_profile.bad_count > 0:
            grade_text = f"{grade_text} / {MSG_QUALITY_OUTLIER_HINT_FMT.format(count=self.state.quality_profile.bad_count)}"
            grade_text = f"{grade_text} / {STATUS_QUALITY_RECOMMENDATION}{MSG_QUALITY_RECOMMEND_OUTLIER}"
        project_text = RESULT_LAST_SAVED_PREFIX + self.state.last_project_file if self.state.last_project_file else RESULT_LAST_SAVED_NONE

        self.status_panel.set_texts(
            step=step,
            files=files,
            points=points,
            mismatch=mismatch,
            quality=quality_text,
            grade=grade_text,
            guide=guide,
            project=project_text,
            message=self._status_message,
        )

    def _set_message(self, text: str, is_error: bool = False) -> None:
        prefix = ERROR_MESSAGE_PREFIX if is_error else ""
        self._status_message = f"{prefix}{text}" if text else ""
        self._refresh_status()

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
            self.state.show_split_compare = False
            self.state.clear_alignment()
            self.chk_compare_flat.setChecked(False)
            self.chk_compare_split.setChecked(False)
            self.slider_flat_intensity.setValue(FLATTEN_PRESET_INTENSITY_DEFAULT)
            self.last_dir = str(Path(file_path).parent)
            self._set_message(MSG_FILE_LOADED_FMT.format(label=VIEW_LABEL_PHOTO, name=Path(file_path).name))
            self._refresh_ui()
        except Exception as exc:
            QMessageBox.warning(self, DIALOG_TITLE_ERROR, MSG_LOAD_PHOTO_ERROR_FMT.format(error=exc))
            self._set_message(f"{MSG_LOAD_PHOTO_ERROR_FMT.format(error=exc)}", is_error=True)

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
            self._set_message(MSG_FILE_LOADED_FMT.format(label=VIEW_LABEL_PLAN, name=Path(file_path).name))
            self._refresh_ui()
        except Exception as exc:
            QMessageBox.warning(self, DIALOG_TITLE_ERROR, MSG_LOAD_PLAN_ERROR_FMT.format(error=exc))
            self._set_message(MSG_LOAD_PLAN_ERROR_FMT.format(error=exc), is_error=True)
