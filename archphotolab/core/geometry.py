from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import cv2
import numpy as np

from archphotolab.constants import (
    ALIGNMENT_MODE_AFFINE,
    ALIGNMENT_MODE_HOMOGRAPHY,
    ALIGNMENT_MODE_SIMILARITY,
    DEFAULT_ALIGNMENT_MODE,
    QUALITY_GRADE_GOOD,
    QUALITY_GRADE_NORMAL,
    QUALITY_GRADE_POOR,
    QUALITY_GRADE_UNKNOWN,
    ERROR_GRADE_GOOD,
    ERROR_GRADE_WARNING,
    ERROR_WARNING_PERCENTILE,
    HOMOGRAPHY_METHOD,
    MIN_ALIGNMENT_POINTS,
    MSG_ALIGNMENT_MODE_UNSUPPORTED,
    MSG_HOMOGRAPHY_BAD_POINT_SHAPE,
    MSG_HOMOGRAPHY_BAD_RESULT,
    MSG_HOMOGRAPHY_DEGENERATE,
    MSG_HOMOGRAPHY_REQUIRE_MIN_POINTS_FMT,
)


def _to_float_points(points: Sequence[Tuple[float, float]]) -> np.ndarray:
    return np.asarray(points, dtype=np.float32)


@dataclass
class AlignmentConfig:
    """Configuration for transform estimation."""

    mode: str = DEFAULT_ALIGNMENT_MODE
    ransac: bool = False
    ransac_reproj_threshold: float = 3.0


@dataclass
class QualityProfile:
    """Compact quality summary for one alignment result."""

    average_error: Optional[float]
    median_error: Optional[float]
    max_error: Optional[float]
    bad_count: int
    grade: str
    inlier_count: int


@dataclass
class AlignmentResult:
    """Result object from alignment estimation."""

    matrix: Optional[np.ndarray]
    used_point_count: int
    reprojection_errors: List[float]
    score: float
    outlier_indices: List[int]
    inlier_mask: Optional[np.ndarray]
    quality_profile: QualityProfile
    mode: str
    error_message: Optional[str] = None


def _validate_point_pairs(
    photo_points: Sequence[Tuple[float, float]],
    plan_points: Sequence[Tuple[float, float]],
) -> Tuple[int, np.ndarray, np.ndarray]:
    use_count = min(len(photo_points), len(plan_points))
    if use_count < MIN_ALIGNMENT_POINTS:
        return use_count, np.empty((0, 2), np.float32), np.empty((0, 2), np.float32)

    src = _to_float_points(plan_points[:use_count]).reshape(-1, 1, 2)
    dst = _to_float_points(photo_points[:use_count]).reshape(-1, 1, 2)
    return use_count, src, dst


def _estimate_homography(src: np.ndarray, dst: np.ndarray, cfg: AlignmentConfig) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    flags = HOMOGRAPHY_METHOD if not cfg.ransac else cv2.RANSAC
    matrix, mask = cv2.findHomography(src, dst, method=flags, ransacReprojThreshold=cfg.ransac_reproj_threshold)
    return matrix, mask


def _estimate_affine(src: np.ndarray, dst: np.ndarray, cfg: AlignmentConfig) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    if cfg.ransac:
        matrix, mask = cv2.estimateAffine2D(
            src.reshape(-1, 1, 2),
            dst.reshape(-1, 1, 2),
            method=cv2.RANSAC,
            ransacReprojThreshold=cfg.ransac_reproj_threshold,
        )
        return matrix, mask

    matrix, _ = cv2.estimateAffine2D(src.reshape(-1, 1, 2), dst.reshape(-1, 1, 2), method=0, ransacReprojThreshold=0)
    return matrix, None


def _estimate_similarity(src: np.ndarray, dst: np.ndarray, cfg: AlignmentConfig) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    if cfg.ransac:
        matrix, mask = cv2.estimateAffinePartial2D(
            src.reshape(-1, 1, 2),
            dst.reshape(-1, 1, 2),
            method=cv2.RANSAC,
            ransacReprojThreshold=cfg.ransac_reproj_threshold,
        )
        return matrix, mask

    matrix, _ = cv2.estimateAffinePartial2D(
        src.reshape(-1, 1, 2),
        dst.reshape(-1, 1, 2),
        method=0,
        ransacReprojThreshold=0,
    )
    return matrix, None


def _project_plan_points(plan_points: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    if matrix is None:
        return np.empty((0, 2), dtype=np.float32)
    src = plan_points.reshape(-1, 1, 2)

    if matrix.shape == (3, 3):
        projected = cv2.perspectiveTransform(src, matrix)
    else:
        projected = cv2.transform(src, matrix)

    return projected.reshape(-1, 2)


def _safe_percentile_threshold(values: Sequence[float]) -> float:
    if not values:
        return float("inf")
    if len(values) < 3:
        return max(values)
    return float(np.percentile(np.asarray(values, dtype=np.float32), ERROR_WARNING_PERCENTILE))


def _mad_threshold(values: Sequence[float]) -> float:
    arr = np.asarray(values, dtype=np.float32)
    if arr.size < 4:
        return float("inf")

    median = float(np.median(arr))
    mad = np.median(np.abs(arr - median))
    if mad <= 1e-6:
        return median * 3.0
    return float(median + 3.4826 * mad)


def _grade_from_errors(errors: Sequence[float]) -> str:
    if not errors:
        return QUALITY_GRADE_UNKNOWN

    arr = np.asarray(errors, dtype=np.float32)
    median = float(np.median(arr))
    mean = float(np.mean(arr))
    if mean <= ERROR_GRADE_GOOD and median <= ERROR_GRADE_GOOD:
        return QUALITY_GRADE_GOOD
    if mean <= ERROR_GRADE_WARNING and median <= ERROR_GRADE_WARNING:
        return QUALITY_GRADE_NORMAL
    return QUALITY_GRADE_POOR


def _build_quality_profile(errors: Sequence[float], inlier_mask: Optional[np.ndarray]) -> QualityProfile:
    if not errors:
        return QualityProfile(
            average_error=None,
            median_error=None,
            max_error=None,
            bad_count=0,
            grade=QUALITY_GRADE_UNKNOWN,
            inlier_count=0,
        )

    arr = np.asarray(errors, dtype=np.float32)
    percentile_threshold = _safe_percentile_threshold(arr.tolist())
    mad_threshold = _mad_threshold(arr.tolist())
    threshold = max(percentile_threshold, mad_threshold, ERROR_GRADE_WARNING)
    outlier_mask = arr > threshold
    bad_count = int(np.sum(outlier_mask))
    return QualityProfile(
        average_error=float(arr.mean()),
        median_error=float(np.median(arr)),
        max_error=float(arr.max()),
        bad_count=bad_count,
        grade=_grade_from_errors(arr.tolist()),
        inlier_count=int(np.sum(inlier_mask.astype(bool).flatten())) if inlier_mask is not None else int(len(arr)),
    )


def _alignment_score(profile: QualityProfile) -> float:
    if profile.average_error is None:
        return 0.0
    error = profile.average_error
    if error <= 0:
        return 1.0
    return float(1.0 / (1.0 + error))


def estimate_transform(
    photo_points: Sequence[Tuple[float, float]],
    plan_points: Sequence[Tuple[float, float]],
    config: AlignmentConfig | None = None,
) -> AlignmentResult:
    """Estimate transformation from plan points to photo points."""
    cfg = config or AlignmentConfig()
    use_count, src, dst = _validate_point_pairs(photo_points, plan_points)

    if use_count < MIN_ALIGNMENT_POINTS:
        return AlignmentResult(
            matrix=None,
            used_point_count=use_count,
            reprojection_errors=[],
            score=0.0,
            outlier_indices=[],
            inlier_mask=None,
            quality_profile=QualityProfile(
                average_error=None,
                median_error=None,
                max_error=None,
                bad_count=0,
                grade=QUALITY_GRADE_UNKNOWN,
                inlier_count=0,
            ),
            mode=cfg.mode,
            error_message=MSG_HOMOGRAPHY_REQUIRE_MIN_POINTS_FMT.format(min_points=MIN_ALIGNMENT_POINTS),
        )

    if src.ndim != 3 or src.shape[0] < MIN_ALIGNMENT_POINTS or src.shape[2] != 2:
        return AlignmentResult(
            matrix=None,
            used_point_count=0,
            reprojection_errors=[],
            score=0.0,
            outlier_indices=[],
            inlier_mask=None,
            quality_profile=QualityProfile(
                average_error=None,
                median_error=None,
                max_error=None,
                bad_count=0,
                grade=QUALITY_GRADE_UNKNOWN,
                inlier_count=0,
            ),
            mode=cfg.mode,
            error_message=MSG_HOMOGRAPHY_BAD_POINT_SHAPE,
        )

    if cfg.mode == ALIGNMENT_MODE_HOMOGRAPHY:
        matrix, inliers = _estimate_homography(src, dst, cfg)
    elif cfg.mode == ALIGNMENT_MODE_AFFINE:
        matrix, inliers = _estimate_affine(src, dst, cfg)
    elif cfg.mode == ALIGNMENT_MODE_SIMILARITY:
        matrix, inliers = _estimate_similarity(src, dst, cfg)
    else:
        return AlignmentResult(
            matrix=None,
            used_point_count=0,
            reprojection_errors=[],
            score=0.0,
            outlier_indices=[],
            inlier_mask=None,
            quality_profile=QualityProfile(
                average_error=None,
                median_error=None,
                max_error=None,
                bad_count=0,
                grade=QUALITY_GRADE_UNKNOWN,
                inlier_count=0,
            ),
            mode=cfg.mode,
            error_message=MSG_ALIGNMENT_MODE_UNSUPPORTED,
        )

    if matrix is None:
        return AlignmentResult(
            matrix=None,
            used_point_count=use_count,
            reprojection_errors=[],
            score=0.0,
            outlier_indices=[],
            inlier_mask=None,
            quality_profile=QualityProfile(
                average_error=None,
                median_error=None,
                max_error=None,
                bad_count=0,
                grade=QUALITY_GRADE_UNKNOWN,
                inlier_count=0,
            ),
            mode=cfg.mode,
            error_message=MSG_HOMOGRAPHY_DEGENERATE,
        )

    if matrix.shape not in [(3, 3), (2, 3)]:
        return AlignmentResult(
            matrix=None,
            used_point_count=use_count,
            reprojection_errors=[],
            score=0.0,
            outlier_indices=[],
            inlier_mask=inliers,
            quality_profile=QualityProfile(
                average_error=None,
                median_error=None,
                max_error=None,
                bad_count=0,
                grade=QUALITY_GRADE_UNKNOWN,
                inlier_count=0,
            ),
            mode=cfg.mode,
            error_message=MSG_HOMOGRAPHY_BAD_RESULT,
        )

    errors = compute_reprojection_errors(
        photo_points=photo_points,
        plan_points=plan_points,
        transform_matrix=matrix,
        used_count=use_count,
    )
    profile = _build_quality_profile(errors, inliers)
    bad_threshold = max(
        _safe_percentile_threshold(errors),
        _mad_threshold(errors),
        ERROR_GRADE_WARNING,
    )
    outliers = [idx for idx, value in enumerate(errors) if value > bad_threshold]
    score = _alignment_score(profile)

    return AlignmentResult(
        matrix=matrix,
        used_point_count=use_count,
        reprojection_errors=errors,
        score=score,
        outlier_indices=outliers,
        inlier_mask=inliers,
        quality_profile=profile,
        mode=cfg.mode,
        error_message=None,
    )


def warp_plan_to_photo(
    plan_image: np.ndarray,
    transform_matrix: np.ndarray,
    photo_shape: Tuple[int, int],
    mode: str = DEFAULT_ALIGNMENT_MODE,
) -> np.ndarray:
    """Warp plan image into photo coordinate space."""
    height, width = photo_shape[:2]

    if transform_matrix is None:
        raise ValueError("transform_matrix is missing")

    if transform_matrix.shape == (3, 3):
        return cv2.warpPerspective(
            plan_image,
            transform_matrix,
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0),
        )

    if transform_matrix.shape == (2, 3):
        return cv2.warpAffine(
            plan_image,
            transform_matrix,
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0),
        )

    if mode == ALIGNMENT_MODE_AFFINE and transform_matrix.shape == (3, 3):
        # 안전장치: 잘못된 모양 데이터가 들어오는 케이스
        affine = transform_matrix[:2, :]
        return cv2.warpAffine(
            plan_image,
            affine,
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0),
        )

    raise ValueError(MSG_HOMOGRAPHY_BAD_RESULT)


def compute_reprojection_errors(
    photo_points: Sequence[Tuple[float, float]],
    plan_points: Sequence[Tuple[float, float]],
    transform_matrix: np.ndarray,
    used_count: Optional[int] = None,
) -> List[float]:
    """Compute per-point reprojection distance errors in photo space."""
    if used_count is None:
        used_count = min(len(photo_points), len(plan_points))
    if used_count <= 0:
        return []

    src = _to_float_points(plan_points[:used_count]).reshape(-1, 1, 2)
    projected = _project_plan_points(src, transform_matrix).reshape(-1, 2)
    target = _to_float_points(photo_points[:used_count])
    errs = np.linalg.norm(projected - target, axis=1)
    return [float(v) for v in errs.tolist()]


def mean_and_max_error(errors: Sequence[float]) -> Tuple[float | None, float | None]:
    if not errors:
        return None, None
    arr = np.asarray(errors, dtype=np.float32)
    return float(arr.mean()), float(arr.max())


def estimate_homography(
    photo_points: Sequence[Tuple[float, float]],
    plan_points: Sequence[Tuple[float, float]],
) -> Tuple[Optional[np.ndarray], Optional[str], int]:
    """Compatibility shim for legacy caller."""
    result = estimate_transform(photo_points, plan_points, AlignmentConfig(mode=ALIGNMENT_MODE_HOMOGRAPHY))
    return result.matrix, result.error_message, result.used_point_count


def evaluate_quality(errors: Sequence[float], outlier_indices: Sequence[int] | None = None) -> dict[str, float | int | str | None]:
    """Return quality values for UI summary."""
    if not errors:
        return {
            "avg": None,
            "median": None,
            "max": None,
            "bad_count": 0,
            "grade": QUALITY_GRADE_UNKNOWN,
        }

    profile = _build_quality_profile(errors, None)
    return {
        "avg": profile.average_error,
        "median": profile.median_error,
        "max": profile.max_error,
        "bad_count": len(list(outlier_indices or [])) if outlier_indices is not None else profile.bad_count,
        "grade": profile.grade,
    }
