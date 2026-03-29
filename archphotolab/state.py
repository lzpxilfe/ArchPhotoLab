from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np

from archphotolab.constants import (
    DEFAULT_ALIGNMENT_MODE,
    POINT_HISTORY_LIMIT,
    POINT_PANEL_ZOOM_DEFAULT,
    FLATTEN_PRESET_RECORD,
    FLATTEN_PRESET_DEFAULT,
    FLATTEN_PRESET_INTENSITY_DEFAULT,
    QUALITY_GRADE_UNKNOWN,
    OVERLAY_ALPHA_DEFAULT,
    SPLIT_VIEW_DEFAULT_RATIO,
    VIEW_MODE_OVERLAY,
    VIEW_MODE_PHOTO,
)


Point = Tuple[float, float]


@dataclass
class AlignmentProfile:
    average_error: Optional[float] = None
    median_error: Optional[float] = None
    max_error: Optional[float] = None
    bad_count: int = 0
    grade: str = QUALITY_GRADE_UNKNOWN
    used_count: int = 0
    score: float = 0.0
    outlier_indices: List[int] = field(default_factory=list)


@dataclass
class PointSnapshot:
    photo_points: List[Point]
    plan_points: List[Point]
    selected_photo_point: Optional[int]
    selected_plan_point: Optional[int]
    alignment_mode: str


def _copy_points(points: List[Point]) -> List[Point]:
    return [(float(x), float(y)) for x, y in points]


@dataclass
class AppState:
    """In-memory state for one active ArchPhotoLab session."""
    photo_path: Optional[str] = None
    plan_path: Optional[str] = None

    photo_points: List[Point] = field(default_factory=list)
    plan_points: List[Point] = field(default_factory=list)

    photo_image: Optional[np.ndarray] = None  # RGB uint8
    plan_image: Optional[np.ndarray] = None  # RGB uint8

    flattened_photo: Optional[np.ndarray] = None  # RGB uint8
    show_flat_photo: bool = False
    flatten_preset: str = FLATTEN_PRESET_DEFAULT
    flatten_intensity: int = FLATTEN_PRESET_INTENSITY_DEFAULT
    show_split_compare: bool = False
    split_ratio: float = SPLIT_VIEW_DEFAULT_RATIO

    homography: Optional[np.ndarray] = None  # 3x3
    warped_plan: Optional[np.ndarray] = None  # RGB uint8 in photo coordinates
    alignment_mode: str = DEFAULT_ALIGNMENT_MODE
    alignment_score: float = 0.0

    overlay_alpha: float = OVERLAY_ALPHA_DEFAULT
    reprojection_errors: List[float] = field(default_factory=list)
    reprojection_avg: Optional[float] = None
    reprojection_max: Optional[float] = None
    reprojection_median: Optional[float] = None
    quality_profile: AlignmentProfile = field(default_factory=AlignmentProfile)
    outlier_indices: List[int] = field(default_factory=list)

    result_view_mode: str = VIEW_MODE_OVERLAY

    selected_photo_point: Optional[int] = None
    selected_plan_point: Optional[int] = None
    selected_point_side: str = VIEW_MODE_PHOTO

    last_project_file: str = ""

    workflow_stage: str = ""
    photo_view_zoom: float = POINT_PANEL_ZOOM_DEFAULT
    photo_view_pan_x: int = 0
    photo_view_pan_y: int = 0
    plan_view_zoom: float = POINT_PANEL_ZOOM_DEFAULT
    plan_view_pan_x: int = 0
    plan_view_pan_y: int = 0
    point_history: List[PointSnapshot] = field(default_factory=list)
    point_redo: List[PointSnapshot] = field(default_factory=list)

    def snapshot_point_state(self) -> PointSnapshot:
        return PointSnapshot(
            photo_points=_copy_points(self.photo_points),
            plan_points=_copy_points(self.plan_points),
            selected_photo_point=self.selected_photo_point,
            selected_plan_point=self.selected_plan_point,
            alignment_mode=self.alignment_mode,
        )

    def __post_init__(self) -> None:
        if not self.point_history:
            self.push_point_history()

    def push_point_history(self) -> None:
        self.point_history.append(self.snapshot_point_state())
        self.point_redo.clear()
        if len(self.point_history) > POINT_HISTORY_LIMIT:
            self.point_history.pop(0)

    def restore_point_snapshot(self, snapshot: PointSnapshot) -> None:
        self.photo_points = _copy_points(snapshot.photo_points)
        self.plan_points = _copy_points(snapshot.plan_points)
        self.selected_photo_point = snapshot.selected_photo_point
        self.selected_plan_point = snapshot.selected_plan_point
        self.alignment_mode = snapshot.alignment_mode

    def undo_point_action(self) -> bool:
        if len(self.point_history) <= 1:
            return False

        current = self.point_history.pop()
        self.point_redo.append(current)
        restored = self.point_history[-1]
        self.restore_point_snapshot(restored)
        self.clear_alignment()
        return True

    def redo_point_action(self) -> bool:
        if not self.point_redo:
            return False

        restored = self.point_redo.pop()
        self.point_history.append(restored)
        self.restore_point_snapshot(restored)
        self.clear_alignment()
        return True

    def clear_alignment(self) -> None:
        self.homography = None
        self.warped_plan = None
        self.reprojection_errors = []
        self.reprojection_avg = None
        self.reprojection_max = None
        self.reprojection_median = None
        self.outlier_indices = []
        self.quality_profile = AlignmentProfile()
        self.alignment_score = 0.0

    def photo_point_count(self) -> int:
        return len(self.photo_points)

    def plan_point_count(self) -> int:
        return len(self.plan_points)

    def clear_points(self) -> None:
        self.photo_points.clear()
        self.plan_points.clear()
        self.clear_alignment()
