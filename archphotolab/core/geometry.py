from __future__ import annotations

from typing import List, Sequence, Tuple

import cv2
import numpy as np

from archphotolab.constants import (
    HOMOGRAPHY_METHOD,
    MIN_ALIGNMENT_POINTS,
    MSG_HOMOGRAPHY_BAD_POINT_SHAPE,
    MSG_HOMOGRAPHY_BAD_RESULT,
    MSG_HOMOGRAPHY_DEGENERATE,
    MSG_HOMOGRAPHY_REQUIRE_MIN_POINTS_FMT,
)


def _to_float_points(points: Sequence[Tuple[float, float]]) -> np.ndarray:
    return np.asarray(points, dtype=np.float32)


def estimate_homography(
    photo_points: Sequence[Tuple[float, float]],
    plan_points: Sequence[Tuple[float, float]],
) -> Tuple[np.ndarray | None, str | None, int]:
    """Estimate homography mapping plan points to photo points.

    Returns
    - homography matrix or None
    - error message or None
    - count of points used
    """
    p_count = len(photo_points)
    q_count = len(plan_points)
    use_count = min(p_count, q_count)
    if use_count < MIN_ALIGNMENT_POINTS:
        return None, MSG_HOMOGRAPHY_REQUIRE_MIN_POINTS_FMT.format(min_points=MIN_ALIGNMENT_POINTS), use_count

    src = _to_float_points(plan_points[:use_count])
    dst = _to_float_points(photo_points[:use_count])

    if src.ndim != 2 or src.shape[0] < 4 or src.shape[1] != 2:
        return None, MSG_HOMOGRAPHY_BAD_POINT_SHAPE, use_count

    H, _mask = cv2.findHomography(src, dst, method=HOMOGRAPHY_METHOD)
    if H is None:
        return None, MSG_HOMOGRAPHY_DEGENERATE, use_count
    if H.shape != (3, 3):
        return None, MSG_HOMOGRAPHY_BAD_RESULT, use_count
    return H, None, use_count


def warp_plan_to_photo(
    plan_image: np.ndarray,
    homography: np.ndarray,
    photo_shape: Tuple[int, int],
) -> np.ndarray:
    """Warp plan image into photo coordinate space using homography."""
    height, width = photo_shape[:2]
    return cv2.warpPerspective(
        plan_image,
        homography,
        (width, height),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0),
    )


def compute_reprojection_errors(
    photo_points: Sequence[Tuple[float, float]],
    plan_points: Sequence[Tuple[float, float]],
    homography: np.ndarray,
) -> List[float]:
    """Compute per-point reprojection distance errors in photo space."""
    use_count = min(len(photo_points), len(plan_points))
    if use_count == 0:
        return []

    src = _to_float_points(plan_points[:use_count]).reshape(-1, 1, 2)
    projected = cv2.perspectiveTransform(src, homography).reshape(-1, 2)
    target = _to_float_points(photo_points[:use_count])
    errs = np.linalg.norm(projected - target, axis=1)
    return [float(v) for v in errs.tolist()]


def mean_and_max_error(errors: Sequence[float]) -> Tuple[float | None, float | None]:
    if not errors:
        return None, None
    arr = np.asarray(errors, dtype=np.float32)
    return float(arr.mean()), float(arr.max())
