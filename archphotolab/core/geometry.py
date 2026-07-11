from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

import cv2
import numpy as np

from archphotolab.constants import (
    ALIGNMENT_MODE_AFFINE,
    ALIGNMENT_MODE_HOMOGRAPHY,
    ALIGNMENT_MODE_SIMILARITY,
    ALIGNMENT_MODE_TPS,
    DEFAULT_ALIGNMENT_MODE,
    ALIGNMENT_RANSAC_THRESHOLD_DEFAULT,
    GEOMETRY_DEFAULT_RANSAC_THRESHOLD,
    GEOMETRY_NUMERIC_EPSILON,
    ALIGNMENT_SCORE_OFFSET,
    MIN_TPS_POINTS,
    MSG_TPS_REQUIRE_MIN_POINTS_FMT,
    MSG_TPS_SCIPY_MISSING,
    QUALITY_GRADE_GOOD,
    QUALITY_GRADE_NORMAL,
    QUALITY_GRADE_POOR,
    QUALITY_GRADE_UNKNOWN,
    ERROR_GRADE_GOOD,
    ERROR_GRADE_WARNING,
    ERROR_WARNING_PERCENTILE,
    HOMOGRAPHY_METHOD,
    MIN_ALIGNMENT_POINTS,
    QUALITY_MAD_SCALE_FACTOR,
    QUALITY_MAD_EMPTY_MULTIPLIER,
    QUALITY_PERCENTILE_SAMPLE_MIN,
    QUALITY_MAD_SAMPLE_MIN,
    MSG_ALIGNMENT_MODE_UNSUPPORTED,
    MSG_HOMOGRAPHY_BAD_POINT_SHAPE,
    MSG_HOMOGRAPHY_BAD_RESULT,
    MSG_HOMOGRAPHY_DEGENERATE,
    MSG_HOMOGRAPHY_REQUIRE_MIN_POINTS_FMT,
    MSG_TRANSFORM_MATRIX_MISSING,
    TRANSFORM_MATRIX_SHAPES,
    TRANSFORM_MATRIX_SHAPE_AFFINE,
    TRANSFORM_MATRIX_SHAPE_HOMOGRAPHY,
    TRANSFORM_MATRIX_SHAPE_TPS,
)


def _to_float_points(points: Sequence[Tuple[float, float]]) -> np.ndarray:
    return np.asarray(points, dtype=np.float32)


@dataclass
class AlignmentConfig:
    """Configuration for transform estimation."""

    mode: str = DEFAULT_ALIGNMENT_MODE
    ransac: bool = False
    ransac_reproj_threshold: float = ALIGNMENT_RANSAC_THRESHOLD_DEFAULT


def _empty_quality_profile() -> QualityProfile:
    return QualityProfile(
        average_error=None,
        median_error=None,
        max_error=None,
        bad_count=0,
        grade=QUALITY_GRADE_UNKNOWN,
        inlier_count=0,
    )


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
    tps_maps: Optional[Tuple[np.ndarray, np.ndarray]] = field(default=None)

    @classmethod
    def failed(
        cls,
        mode: str,
        error_message: str,
        used_point_count: int = 0,
        inlier_mask: Optional[np.ndarray] = None,
    ) -> AlignmentResult:
        return cls(
            matrix=None,
            used_point_count=used_point_count,
            reprojection_errors=[],
            score=0.0,
            outlier_indices=[],
            inlier_mask=inlier_mask,
            quality_profile=_empty_quality_profile(),
            mode=mode,
            error_message=error_message,
        )


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


def _estimate_tps(
    src_points: Sequence[Tuple[float, float]],
    dst_points: Sequence[Tuple[float, float]],
    photo_shape: Tuple[int, int],
) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[str]]:
    """Estimate TPS warp maps using scipy RBFInterpolator (thin plate spline kernel).

    Returns (remap_x, remap_y, error_message). On success error_message is None.
    """
    try:
        from scipy.interpolate import RBFInterpolator
    except ImportError:
        return None, None, MSG_TPS_SCIPY_MISSING

    src = np.asarray(src_points, dtype=np.float64)  # plan control points
    dst = np.asarray(dst_points, dtype=np.float64)  # photo control points

    # Build RBF from photo-space -> plan-space (inverse mapping for remap)
    # We want: for each photo pixel (px, py), find which plan pixel to sample
    rbf_x = RBFInterpolator(dst, src[:, 0], kernel="thin_plate_spline", smoothing=0.0)
    rbf_y = RBFInterpolator(dst, src[:, 1], kernel="thin_plate_spline", smoothing=0.0)

    h, w = photo_shape[:2]
    grid_y, grid_x = np.mgrid[0:h, 0:w]
    query = np.column_stack([grid_x.ravel().astype(np.float64), grid_y.ravel().astype(np.float64)])

    remap_x = rbf_x(query).reshape(h, w).astype(np.float32)
    remap_y = rbf_y(query).reshape(h, w).astype(np.float32)
    return remap_x, remap_y, None


def _estimate_affine(src: np.ndarray, dst: np.ndarray, cfg: AlignmentConfig) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
    if cfg.ransac:
        matrix, mask = cv2.estimateAffine2D(
            src.reshape(-1, 1, 2),
            dst.reshape(-1, 1, 2),
            method=cv2.RANSAC,
            ransacReprojThreshold=cfg.ransac_reproj_threshold,
        )
        return matrix, mask

    matrix, _ = cv2.estimateAffine2D(
        src.reshape(-1, 1, 2),
        dst.reshape(-1, 1, 2),
        method=HOMOGRAPHY_METHOD,
        ransacReprojThreshold=GEOMETRY_DEFAULT_RANSAC_THRESHOLD,
    )
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
        method=HOMOGRAPHY_METHOD,
        ransacReprojThreshold=GEOMETRY_DEFAULT_RANSAC_THRESHOLD,
    )
    return matrix, None


def _project_plan_points(plan_points: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    if matrix is None:
        return np.empty((0, 2), dtype=np.float32)
    src = plan_points.reshape(-1, 1, 2)

    if matrix.shape == TRANSFORM_MATRIX_SHAPE_HOMOGRAPHY:
        projected = cv2.perspectiveTransform(src, matrix)
    else:
        projected = cv2.transform(src, matrix)

    return projected.reshape(-1, 2)


def _safe_percentile_threshold(values: Sequence[float]) -> float:
    if not values:
        return float("inf")
    if len(values) < QUALITY_PERCENTILE_SAMPLE_MIN:
        return max(values)
    return float(np.percentile(np.asarray(values, dtype=np.float32), ERROR_WARNING_PERCENTILE))


def _mad_threshold(values: Sequence[float]) -> float:
    arr = np.asarray(values, dtype=np.float32)
    if arr.size < QUALITY_MAD_SAMPLE_MIN:
        return float("inf")

    median = float(np.median(arr))
    mad = np.median(np.abs(arr - median))
    if mad <= GEOMETRY_NUMERIC_EPSILON:
        return median * QUALITY_MAD_EMPTY_MULTIPLIER
    return float(median + QUALITY_MAD_SCALE_FACTOR * mad)


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
        return _empty_quality_profile()

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
        return ALIGNMENT_SCORE_OFFSET
    return float(ALIGNMENT_SCORE_OFFSET / (ALIGNMENT_SCORE_OFFSET + error))


def estimate_transform(
    photo_points: Sequence[Tuple[float, float]],
    plan_points: Sequence[Tuple[float, float]],
    config: AlignmentConfig | None = None,
) -> AlignmentResult:
    """Estimate transformation from plan points to photo points."""
    cfg = config or AlignmentConfig()
    use_count, src, dst = _validate_point_pairs(photo_points, plan_points)

    if use_count < MIN_ALIGNMENT_POINTS:
        return AlignmentResult.failed(
            mode=cfg.mode,
            error_message=MSG_HOMOGRAPHY_REQUIRE_MIN_POINTS_FMT.format(min_points=MIN_ALIGNMENT_POINTS),
            used_point_count=use_count,
        )

    if src.ndim != 3 or src.shape[0] < MIN_ALIGNMENT_POINTS or src.shape[2] != 2:
        return AlignmentResult.failed(
            mode=cfg.mode,
            error_message=MSG_HOMOGRAPHY_BAD_POINT_SHAPE,
        )

    if cfg.mode == ALIGNMENT_MODE_HOMOGRAPHY:
        matrix, inliers = _estimate_homography(src, dst, cfg)
    elif cfg.mode == ALIGNMENT_MODE_AFFINE:
        matrix, inliers = _estimate_affine(src, dst, cfg)
    elif cfg.mode == ALIGNMENT_MODE_SIMILARITY:
        matrix, inliers = _estimate_similarity(src, dst, cfg)
    elif cfg.mode == ALIGNMENT_MODE_TPS:
        if use_count < MIN_TPS_POINTS:
            return AlignmentResult.failed(
                mode=cfg.mode,
                error_message=MSG_TPS_REQUIRE_MIN_POINTS_FMT.format(min_points=MIN_TPS_POINTS),
                used_point_count=use_count,
            )
        photo_pts = list(photo_points[:use_count])
        plan_pts = list(plan_points[:use_count])
        # Use a placeholder photo_shape — actual remap computed during warp
        remap_x, remap_y, tps_err = _estimate_tps(
            src_points=plan_pts,
            dst_points=photo_pts,
            photo_shape=(1, 1),  # placeholder; real shape given at warp time
        )
        if tps_err is not None:
            return AlignmentResult.failed(mode=cfg.mode, error_message=tps_err, used_point_count=use_count)
        # Store control points as sentinel matrix; real warp done in warp_plan_to_photo
        sentinel = np.array(TRANSFORM_MATRIX_SHAPE_TPS, dtype=np.float32).reshape(1, 1)
        errors = _tps_reprojection_errors(photo_pts, plan_pts)
        profile = _build_quality_profile(errors, None)
        bad_threshold = max(_safe_percentile_threshold(errors), _mad_threshold(errors), ERROR_GRADE_WARNING)
        outliers = [idx for idx, v in enumerate(errors) if v > bad_threshold]
        score = _alignment_score(profile)
        return AlignmentResult(
            matrix=sentinel,
            used_point_count=use_count,
            reprojection_errors=errors,
            score=score,
            outlier_indices=outliers,
            inlier_mask=None,
            quality_profile=profile,
            mode=cfg.mode,
            error_message=None,
            tps_maps=None,  # computed lazily at warp time
        )
    else:
        return AlignmentResult.failed(
            mode=cfg.mode,
            error_message=MSG_ALIGNMENT_MODE_UNSUPPORTED,
        )

    if matrix is None:
        return AlignmentResult.failed(
            mode=cfg.mode,
            error_message=MSG_HOMOGRAPHY_DEGENERATE,
            used_point_count=use_count,
        )

    if matrix.shape not in TRANSFORM_MATRIX_SHAPES:
        return AlignmentResult.failed(
            mode=cfg.mode,
            error_message=MSG_HOMOGRAPHY_BAD_RESULT,
            used_point_count=use_count,
            inlier_mask=inliers,
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
    photo_points: Optional[Sequence[Tuple[float, float]]] = None,
    plan_points: Optional[Sequence[Tuple[float, float]]] = None,
) -> np.ndarray:
    """Warp plan image into photo coordinate space."""
    height, width = photo_shape[:2]

    if transform_matrix is None:
        raise ValueError(MSG_TRANSFORM_MATRIX_MISSING)

    if mode == ALIGNMENT_MODE_TPS:
        # TPS: compute remap maps fresh with the actual photo size
        if photo_points is None or plan_points is None:
            raise ValueError(MSG_TRANSFORM_MATRIX_MISSING)
        remap_x, remap_y, tps_err = _estimate_tps(
            src_points=list(plan_points),
            dst_points=list(photo_points),
            photo_shape=photo_shape,
        )
        if tps_err is not None:
            raise ValueError(tps_err)
        return cv2.remap(
            plan_image,
            remap_x,
            remap_y,
            interpolation=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0),
        )

    if transform_matrix.shape == TRANSFORM_MATRIX_SHAPE_HOMOGRAPHY:
        return cv2.warpPerspective(
            plan_image,
            transform_matrix,
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0),
        )

    if transform_matrix.shape == TRANSFORM_MATRIX_SHAPE_AFFINE:
        return cv2.warpAffine(
            plan_image,
            transform_matrix,
            (width, height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0),
        )

    raise ValueError(MSG_HOMOGRAPHY_BAD_RESULT)


def warp_validity_mask(
    plan_shape: Tuple[int, int],
    transform_matrix: np.ndarray,
    photo_shape: Tuple[int, int],
    mode: str = DEFAULT_ALIGNMENT_MODE,
    photo_points: Optional[Sequence[Tuple[float, float]]] = None,
    plan_points: Optional[Sequence[Tuple[float, float]]] = None,
) -> np.ndarray:
    """Return a grayscale mask (uint8) in photo coordinate space.

    Pixels that are inside the warped plan boundary = 255.
    Pixels that are outside (border fill) = 0.
    Used by multiply blend to avoid darkening areas outside the plan.
    """
    # Create a solid white single-channel mask the same size as the plan
    h_p, w_p = plan_shape[:2]
    mask_src = np.full((h_p, w_p), 255, dtype=np.uint8)

    height, width = photo_shape[:2]

    if mode == ALIGNMENT_MODE_TPS:
        if photo_points is None or plan_points is None:
            return np.full((height, width), 255, dtype=np.uint8)
        remap_x, remap_y, tps_err = _estimate_tps(
            src_points=list(plan_points),
            dst_points=list(photo_points),
            photo_shape=photo_shape,
        )
        if tps_err is not None:
            return np.full((height, width), 255, dtype=np.uint8)
        return cv2.remap(
            mask_src,
            remap_x,
            remap_y,
            interpolation=cv2.INTER_NEAREST,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0,
        )

    if transform_matrix is None:
        return np.full((height, width), 255, dtype=np.uint8)

    if transform_matrix.shape == TRANSFORM_MATRIX_SHAPE_HOMOGRAPHY:
        return cv2.warpPerspective(
            mask_src,
            transform_matrix,
            (width, height),
            flags=cv2.INTER_NEAREST,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0,
        )

    if transform_matrix.shape == TRANSFORM_MATRIX_SHAPE_AFFINE:
        return cv2.warpAffine(
            mask_src,
            transform_matrix,
            (width, height),
            flags=cv2.INTER_NEAREST,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0,
        )

    return np.full((height, width), 255, dtype=np.uint8)


def _tps_reprojection_errors(
    photo_points: Sequence[Tuple[float, float]],
    plan_points: Sequence[Tuple[float, float]],
) -> List[float]:
    """Placeholder reprojection error for TPS: uses leave-one-out Euclidean distance."""
    if len(photo_points) < 2:
        return [0.0] * len(photo_points)
    errors = []
    for i in range(len(photo_points)):
        other_photo = [p for j, p in enumerate(photo_points) if j != i]
        other_plan = [p for j, p in enumerate(plan_points) if j != i]
        px, py = photo_points[i]
        pl_x, pl_y = plan_points[i]
        # Simple nearest-neighbour residual estimate
        dists = [
            ((px - op[0])**2 + (py - op[1])**2)**0.5
            for op in other_photo
        ]
        errors.append(min(dists) if dists else 0.0)
    return errors


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
