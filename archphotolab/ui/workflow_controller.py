from __future__ import annotations

from typing import Optional

from archphotolab.constants import (
    DEFAULT_ALIGNMENT_MODE,
    MSG_QUALITY_RECOMMEND_OUTLIER,
    QUALITY_GRADE_UNKNOWN,
    MSG_POINT_HISTORY_EMPTY,
    MSG_POINT_HISTORY_REDO_EMPTY,
)
from archphotolab.constants import TRANSFORM_MODE_OPTIONS
from archphotolab.constants import (
    MSG_ALIGNMENT_REQUIRE_IMAGES,
    MSG_ALIGNMENT_REQUIRE_POINTS_FMT,
    MSG_ALIGNMENT_RESULT_INVALID,
    WORKFLOW_ALIGNMENT_EXCLUDE_SUFFIX,
    MIN_ALIGNMENT_POINTS,
    WORKFLOW_STAGE_ALIGNMENT,
    WORKFLOW_STAGE_POINTS,
)
from archphotolab.constants import MSG_ALIGNMENT_MODE_UNSUPPORTED
from archphotolab.constants import VIEW_MODE_PHOTO, VIEW_MODE_PLAN
from archphotolab.core.geometry import AlignmentConfig, AlignmentResult, AlignmentProfile, estimate_transform, warp_plan_to_photo
from archphotolab.state import AlignmentProfile as StateAlignmentProfile, AppState


class WorkflowController:
    """UI-agnostic service layer for point editing and alignment."""

    def __init__(self, state: AppState) -> None:
        self.state = state

    def _clamp_point(self, point: tuple[float, float], width: int, height: int) -> tuple[float, float]:
        x = max(0.0, min(float(point[0]), max(width - 1, 0)))
        y = max(0.0, min(float(point[1]), max(height - 1, 0)))
        return x, y

    def set_alignment_mode(self, mode: str) -> None:
        if mode not in TRANSFORM_MODE_OPTIONS:
            self.state.alignment_mode = DEFAULT_ALIGNMENT_MODE
            raise ValueError(MSG_ALIGNMENT_MODE_UNSUPPORTED)

        if mode != self.state.alignment_mode:
            self.state.alignment_mode = mode
            self.state.workflow_stage = WORKFLOW_STAGE_ALIGNMENT
            self.state.clear_alignment()

    def add_point(self, side: str, x: float, y: float, image_width: int, image_height: int) -> None:
        self.state.push_point_history()

        image_width = max(int(image_width), 1)
        image_height = max(int(image_height), 1)
        point = self._clamp_point((x, y), image_width, image_height)

        if side == VIEW_MODE_PHOTO:
            self.state.photo_points.append(point)
            self.state.selected_photo_point = len(self.state.photo_points) - 1
            self.state.selected_plan_point = None
            self.state.selected_point_side = VIEW_MODE_PHOTO
        else:
            self.state.plan_points.append(point)
            self.state.selected_plan_point = len(self.state.plan_points) - 1
            self.state.selected_photo_point = None
            self.state.selected_point_side = VIEW_MODE_PLAN
        self.state.workflow_stage = WORKFLOW_STAGE_POINTS
        self.state.clear_alignment()

    def move_point(
        self,
        side: str,
        index: int,
        x: float,
        y: float,
        image_width: int,
        image_height: int,
        record_history: bool = False,
    ) -> None:
        points = self.state.photo_points if side == VIEW_MODE_PHOTO else self.state.plan_points
        if index < 0 or index >= len(points):
            return

        if record_history:
            self.state.push_point_history()

        point = self._clamp_point((x, y), max(int(image_width), 1), max(int(image_height), 1))
        points[index] = point

        if side == VIEW_MODE_PHOTO:
            self.state.selected_photo_point = index
            self.state.selected_plan_point = None
            self.state.selected_point_side = VIEW_MODE_PHOTO
        else:
            self.state.selected_plan_point = index
            self.state.selected_photo_point = None
            self.state.selected_point_side = VIEW_MODE_PLAN
        self.state.workflow_stage = WORKFLOW_STAGE_POINTS

        self.state.clear_alignment()

    def _build_alignment_inputs(
        self,
        excluded_indices: Optional[set[int]] = None,
    ) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
        excluded_indices = set(excluded_indices or [])
        photo_points: list[tuple[float, float]] = []
        plan_points: list[tuple[float, float]] = []

        max_count = min(len(self.state.photo_points), len(self.state.plan_points))
        for idx in range(max_count):
            if idx in excluded_indices:
                continue
            photo_points.append(self.state.photo_points[idx])
            plan_points.append(self.state.plan_points[idx])

        return photo_points, plan_points

    def remove_point(self, side: str, index: int) -> None:
        points = self.state.photo_points if side == VIEW_MODE_PHOTO else self.state.plan_points
        if index < 0 or index >= len(points):
            return

        self.state.push_point_history()
        points.pop(index)

        if side == VIEW_MODE_PHOTO:
            self.state.selected_photo_point = None
        else:
            self.state.selected_plan_point = None

        self.state.workflow_stage = WORKFLOW_STAGE_POINTS
        self.state.clear_alignment()

    def reorder_point(self, side: str, direction: int) -> None:
        points = self.state.photo_points if side == VIEW_MODE_PHOTO else self.state.plan_points
        selected = self.state.selected_photo_point if side == VIEW_MODE_PHOTO else self.state.selected_plan_point
        if selected is None or not (0 <= selected < len(points)):
            return

        target = selected + direction
        if target < 0 or target >= len(points):
            return

        self.state.push_point_history()
        points[selected], points[target] = points[target], points[selected]

        if side == VIEW_MODE_PHOTO:
            self.state.selected_photo_point = target
        else:
            self.state.selected_plan_point = target

        self.state.workflow_stage = WORKFLOW_STAGE_POINTS
        self.state.clear_alignment()

    def select_point(self, side: str, index: int) -> None:
        if side == VIEW_MODE_PHOTO:
            self.state.selected_photo_point = index
            self.state.selected_plan_point = None
            self.state.selected_point_side = VIEW_MODE_PHOTO
        else:
            self.state.selected_plan_point = index
            self.state.selected_photo_point = None
            self.state.selected_point_side = VIEW_MODE_PLAN
        self.state.workflow_stage = WORKFLOW_STAGE_POINTS

    def undo_point(self) -> None:
        if not self.state.undo_point_action():
            raise RuntimeError(MSG_POINT_HISTORY_EMPTY)
        self.state.workflow_stage = WORKFLOW_STAGE_POINTS

    def redo_point(self) -> None:
        if not self.state.redo_point_action():
            raise RuntimeError(MSG_POINT_HISTORY_REDO_EMPTY)
        self.state.workflow_stage = WORKFLOW_STAGE_POINTS

    def run_alignment(
        self,
        excluded_indices: Optional[set[int]] = None,
    ) -> tuple[bool, AlignmentResult, Optional[str]]:
        if self.state.photo_image is None or self.state.plan_image is None:
            return False, AlignmentResult(
                matrix=None,
                used_point_count=0,
                reprojection_errors=[],
                score=0.0,
                outlier_indices=[],
                inlier_mask=None,
                quality_profile=AlignmentProfile(
                    average_error=None,
                    median_error=None,
                    max_error=None,
                    bad_count=0,
                    grade=QUALITY_GRADE_UNKNOWN,
                    inlier_count=0,
                ),
                mode=self.state.alignment_mode,
                error_message=MSG_ALIGNMENT_REQUIRE_IMAGES,
            ), MSG_ALIGNMENT_REQUIRE_IMAGES

        photo_points, plan_points = self._build_alignment_inputs(excluded_indices)

        if len(photo_points) < MIN_ALIGNMENT_POINTS or len(plan_points) < MIN_ALIGNMENT_POINTS:
            msg = MSG_ALIGNMENT_REQUIRE_POINTS_FMT.format(min_points=MIN_ALIGNMENT_POINTS)
            return (
                False,
                AlignmentResult(
                    matrix=None,
                    used_point_count=0,
                    reprojection_errors=[],
                    score=0.0,
                    outlier_indices=[],
                    inlier_mask=None,
                    quality_profile=AlignmentProfile(
                        average_error=None,
                        median_error=None,
                        max_error=None,
                        bad_count=0,
                        grade=QUALITY_GRADE_UNKNOWN,
                        inlier_count=0,
                    ),
                    mode=self.state.alignment_mode,
                    error_message=msg,
                ),
                msg,
            )

        if excluded_indices:
            self.state.workflow_stage = f"{WORKFLOW_STAGE_ALIGNMENT}{WORKFLOW_ALIGNMENT_EXCLUDE_SUFFIX}"
        else:
            self.state.workflow_stage = WORKFLOW_STAGE_ALIGNMENT

        config = AlignmentConfig(mode=self.state.alignment_mode)
        result = estimate_transform(photo_points, plan_points, config=config)

        if result.error_message is not None:
            self.state.clear_alignment()
            return False, result, result.error_message

        if result.matrix is None:
            self.state.clear_alignment()
            return False, result, result.error_message or MSG_ALIGNMENT_RESULT_INVALID

        self.state.homography = result.matrix
        self.state.alignment_score = result.score
        self.state.reprojection_errors = result.reprojection_errors
        self.state.reprojection_avg = result.quality_profile.average_error
        self.state.reprojection_median = result.quality_profile.median_error
        self.state.reprojection_max = result.quality_profile.max_error
        self.state.outlier_indices = result.outlier_indices
        self.state.quality_profile = StateAlignmentProfile(
            average_error=result.quality_profile.average_error,
            median_error=result.quality_profile.median_error,
            max_error=result.quality_profile.max_error,
            bad_count=result.quality_profile.bad_count,
            grade=result.quality_profile.grade,
            used_count=result.quality_profile.inlier_count,
            score=result.score,
            outlier_indices=result.outlier_indices,
        )

        self.state.warped_plan = warp_plan_to_photo(
            self.state.plan_image,
            self.state.homography,
            self.state.photo_image.shape,
            mode=self.state.alignment_mode,
        )

        return True, result, None

    def _selected_pair_index(self) -> Optional[int]:
        if self.state.selected_point_side == VIEW_MODE_PHOTO:
            if self.state.selected_photo_point is None:
                return None
            if (
                self.state.selected_plan_point is not None
                and self.state.selected_plan_point != self.state.selected_photo_point
            ):
                return None
            return self.state.selected_photo_point

        if self.state.selected_point_side == VIEW_MODE_PLAN:
            if self.state.selected_plan_point is None:
                return None
            if (
                self.state.selected_photo_point is not None
                and self.state.selected_photo_point != self.state.selected_plan_point
            ):
                return None
            return self.state.selected_plan_point

        return None

    def run_alignment_excluding_selected_pair(self) -> tuple[bool, AlignmentResult, Optional[str]]:
        pair_idx = self._selected_pair_index()
        if pair_idx is None:
            return False, AlignmentResult(
                matrix=None,
                used_point_count=0,
                reprojection_errors=[],
                score=0.0,
                outlier_indices=[],
                inlier_mask=None,
                quality_profile=AlignmentProfile(
                    average_error=None,
                    median_error=None,
                    max_error=None,
                    bad_count=0,
                    grade=QUALITY_GRADE_UNKNOWN,
                    inlier_count=0,
                ),
                mode=self.state.alignment_mode,
                error_message=MSG_QUALITY_RECOMMEND_OUTLIER,
            ), MSG_QUALITY_RECOMMEND_OUTLIER

        return self.run_alignment(excluded_indices={pair_idx})
