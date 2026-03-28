from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import numpy as np


Point = Tuple[float, float]


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

    homography: Optional[np.ndarray] = None  # 3x3
    warped_plan: Optional[np.ndarray] = None  # RGB uint8 in photo coordinates

    overlay_alpha: float = 0.45
    reprojection_errors: List[float] = field(default_factory=list)
    reprojection_avg: Optional[float] = None
    reprojection_max: Optional[float] = None

    result_view_mode: str = "overlay"

    selected_photo_point: Optional[int] = None
    selected_plan_point: Optional[int] = None
    selected_point_side: str = "photo"

    last_project_file: str = ""

    def clear_alignment(self) -> None:
        self.homography = None
        self.warped_plan = None
        self.reprojection_errors = []
        self.reprojection_avg = None
        self.reprojection_max = None

    @staticmethod
    def _point_tuple_list(points: List[Point]) -> List[tuple]:
        return [(float(x), float(y)) for x, y in points]

    def photo_point_count(self) -> int:
        return len(self.photo_points)

    def plan_point_count(self) -> int:
        return len(self.plan_points)

    def clear_points(self) -> None:
        self.photo_points.clear()
        self.plan_points.clear()
        self.clear_alignment()
