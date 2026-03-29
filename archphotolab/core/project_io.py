from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from archphotolab.constants import (
    APP_VERSION,
    DEFAULT_ALIGNMENT_MODE,
    OVERLAY_ALPHA_DEFAULT,
    POINT_PANEL_ZOOM_DEFAULT,
    MSG_PROJECT_VERSION_UPGRADE_FMT,
    FLATTEN_PRESET_DEFAULT,
    FLATTEN_PRESET_INTENSITY_DEFAULT,
    FLATTEN_PRESET_INTENSITY_MAX,
    FLATTEN_PRESET_INTENSITY_MIN,
    FLATTEN_PRESET_KEYS,
    MSG_PROJECT_FORMAT_INVALID,
    MSG_PROJECT_MISSING_PATH_FMT,
    JSON_CHARSET_ENCODING,
    PROJECT_MIN_COMPATIBLE_VERSION,
    QUALITY_GRADE_UNKNOWN,
    SPLIT_VIEW_DEFAULT_RATIO,
    SPLIT_VIEW_MAX_RATIO,
    SPLIT_VIEW_MIN_RATIO,
    TRANSFORM_MODE_OPTIONS,
    TRANSFORM_MATRIX_SHAPES,
    VIEW_MODE_OVERLAY,
    ProjectKeys,
)
from archphotolab.state import AlignmentProfile, AppState


def _normalize_version(value: Any) -> str:
    if not isinstance(value, str):
        return PROJECT_MIN_COMPATIBLE_VERSION
    normalized = value.strip()
    return normalized if normalized else PROJECT_MIN_COMPATIBLE_VERSION


def _version_tuple(value: str) -> Tuple[int, ...]:
    parts: List[int] = []
    for part in value.split("."):
        if part.isdigit():
            parts.append(int(part))
        else:
            parts.append(0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def _coerce_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


PROJECT_FORMAT = APP_VERSION


def load_project(path: str) -> Dict[str, Any]:
    """Load raw project dictionary from JSON file."""
    with open(path, "r", encoding=JSON_CHARSET_ENCODING) as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(MSG_PROJECT_FORMAT_INVALID)
    return data


def parse_points(value: Any) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    if not isinstance(value, list):
        return points

    for item in value:
        if isinstance(item, dict) and "x" in item and "y" in item:
            try:
                points.append((float(item["x"]), float(item["y"])))
            except (TypeError, ValueError):
                continue
            continue

        if isinstance(item, (list, tuple)) and len(item) == 2:
            try:
                points.append((float(item[0]), float(item[1])))
            except (TypeError, ValueError):
                continue
    return points


def parse_alignment_profile(value: Any) -> AlignmentProfile:
    if not isinstance(value, dict):
        return AlignmentProfile()
    return AlignmentProfile(
        average_error=value.get("avg"),
        median_error=value.get("median"),
        max_error=value.get("max"),
        bad_count=int(value.get("bad_count") or 0),
        grade=value.get("grade") or QUALITY_GRADE_UNKNOWN,
        used_count=int(value.get("used_count") or 0),
        score=float(value.get("score") or 0.0),
        outlier_indices=[int(v) for v in (value.get("outlier_indices") or []) if isinstance(v, (int, float))],
    )


def parse_homography(value: Any):
    if value is None or not isinstance(value, list):
        return None
    arr = np.array(value, dtype=float)
    if arr.shape not in TRANSFORM_MATRIX_SHAPES:
        return None
    return arr


def migrate_project_payload(raw: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Fill missing keys for older versions and return migration warning list."""
    payload = dict(raw)
    warnings: List[str] = []

    loaded_version = _normalize_version(payload.get(ProjectKeys.FORMAT_VERSION))
    current = _normalize_version(APP_VERSION)
    if _version_tuple(loaded_version) < _version_tuple(current):
        warnings.append(
            MSG_PROJECT_VERSION_UPGRADE_FMT.format(from_version=loaded_version, to_version=current),
        )

    payload.setdefault(ProjectKeys.FORMAT_VERSION, PROJECT_FORMAT)
    payload.setdefault(ProjectKeys.PHOTO_PATH, None)
    payload.setdefault(ProjectKeys.PLAN_PATH, None)
    payload.setdefault(ProjectKeys.PHOTO_POINTS, [])
    payload.setdefault(ProjectKeys.PLAN_POINTS, [])
    payload.setdefault(ProjectKeys.ALIGNMENT_MODE, DEFAULT_ALIGNMENT_MODE)
    payload.setdefault(ProjectKeys.FLATTEN_PRESET, FLATTEN_PRESET_DEFAULT)
    payload.setdefault(ProjectKeys.FLATTEN_INTENSITY, FLATTEN_PRESET_INTENSITY_DEFAULT)
    payload.setdefault(ProjectKeys.SHOW_FLAT_PHOTO, False)
    payload.setdefault(ProjectKeys.SHOW_SPLIT_VIEW, False)
    payload.setdefault(ProjectKeys.SPLIT_VIEW_RATIO, SPLIT_VIEW_DEFAULT_RATIO)
    payload.setdefault(ProjectKeys.RESULT_VIEW_MODE, VIEW_MODE_OVERLAY)
    payload.setdefault(ProjectKeys.OVERLAY_ALPHA, OVERLAY_ALPHA_DEFAULT)
    payload.setdefault(ProjectKeys.HOMOGRAPHY, None)
    payload.setdefault(ProjectKeys.REPROJECTION_AVG, None)
    payload.setdefault(ProjectKeys.REPROJECTION_MEDIAN, None)
    payload.setdefault(ProjectKeys.REPROJECTION_MAX, None)
    payload.setdefault(ProjectKeys.REPROJECTION_ERRORS, [])
    payload.setdefault(ProjectKeys.WORKFLOW_STAGE, "")
    payload.setdefault(ProjectKeys.PHOTO_VIEW_ZOOM, POINT_PANEL_ZOOM_DEFAULT)
    payload.setdefault(ProjectKeys.PHOTO_VIEW_PAN_X, 0)
    payload.setdefault(ProjectKeys.PHOTO_VIEW_PAN_Y, 0)
    payload.setdefault(ProjectKeys.PLAN_VIEW_ZOOM, POINT_PANEL_ZOOM_DEFAULT)
    payload.setdefault(ProjectKeys.PLAN_VIEW_PAN_X, 0)
    payload.setdefault(ProjectKeys.PLAN_VIEW_PAN_Y, 0)
    payload.setdefault(ProjectKeys.POINT_EDITOR_STATE, {})
    payload.setdefault(ProjectKeys.QUALITY_PROFILE, {})
    payload.setdefault(ProjectKeys.QUALITY_GRADE, QUALITY_GRADE_UNKNOWN)
    payload.setdefault(ProjectKeys.FLATTEN_ENABLED, False)

    if payload[ProjectKeys.FLATTEN_INTENSITY] is None:
        payload[ProjectKeys.FLATTEN_INTENSITY] = FLATTEN_PRESET_INTENSITY_DEFAULT

    if not isinstance(payload.get(ProjectKeys.SPLIT_VIEW_RATIO), (int, float)):
        payload[ProjectKeys.SPLIT_VIEW_RATIO] = SPLIT_VIEW_DEFAULT_RATIO
    payload[ProjectKeys.SPLIT_VIEW_RATIO] = float(np.clip(
        _coerce_float(payload[ProjectKeys.SPLIT_VIEW_RATIO], SPLIT_VIEW_DEFAULT_RATIO),
        SPLIT_VIEW_MIN_RATIO,
        SPLIT_VIEW_MAX_RATIO,
    ))

    if payload[ProjectKeys.FLATTEN_PRESET] not in FLATTEN_PRESET_KEYS:
        payload[ProjectKeys.FLATTEN_PRESET] = FLATTEN_PRESET_DEFAULT

    intensity = _coerce_int(payload.get(ProjectKeys.FLATTEN_INTENSITY), FLATTEN_PRESET_INTENSITY_DEFAULT)
    payload[ProjectKeys.FLATTEN_INTENSITY] = int(np.clip(intensity, FLATTEN_PRESET_INTENSITY_MIN, FLATTEN_PRESET_INTENSITY_MAX))

    alignment_mode = payload.get(ProjectKeys.ALIGNMENT_MODE, DEFAULT_ALIGNMENT_MODE)
    if alignment_mode not in TRANSFORM_MODE_OPTIONS:
        payload[ProjectKeys.ALIGNMENT_MODE] = DEFAULT_ALIGNMENT_MODE

    return payload, warnings


def resolve_saved_image_path(
    saved_path: Optional[str],
    project_file: str,
    fallback_dirs: Optional[List[str]] = None,
) -> Optional[str]:
    if not saved_path:
        return None

    fallback_dirs = fallback_dirs or []
    project_dir = Path(project_file).resolve().parent
    filename = Path(saved_path).name

    candidates: list[str] = []
    if os.path.isabs(saved_path):
        candidates.append(saved_path)
    else:
        candidates.append(str(project_dir / saved_path))

    candidates.append(str(Path(saved_path).expanduser()))
    candidates.append(str(Path.home() / filename))
    search_dirs = [str(project_dir), os.getcwd(), *fallback_dirs]
    for directory in search_dirs:
        if directory:
            candidates.append(str(Path(directory).expanduser() / filename))

    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return os.path.abspath(candidate)
    return None


def state_to_dict(state: AppState) -> Dict[str, Any]:
    return {
        ProjectKeys.FORMAT_VERSION: PROJECT_FORMAT,
        ProjectKeys.PHOTO_PATH: state.photo_path,
        ProjectKeys.PLAN_PATH: state.plan_path,
        ProjectKeys.PHOTO_POINTS: [{"x": float(x), "y": float(y)} for x, y in state.photo_points],
        ProjectKeys.PLAN_POINTS: [{"x": float(x), "y": float(y)} for x, y in state.plan_points],
        ProjectKeys.ALIGNMENT_MODE: state.alignment_mode,
        ProjectKeys.FLATTEN_PRESET: state.flatten_preset,
        ProjectKeys.FLATTEN_INTENSITY: state.flatten_intensity,
        ProjectKeys.SHOW_FLAT_PHOTO: bool(state.show_flat_photo),
        ProjectKeys.SHOW_SPLIT_VIEW: bool(state.show_split_compare),
        ProjectKeys.SPLIT_VIEW_RATIO: float(state.split_ratio),
        ProjectKeys.RESULT_VIEW_MODE: state.result_view_mode,
        ProjectKeys.OVERLAY_ALPHA: float(state.overlay_alpha),
        ProjectKeys.HOMOGRAPHY: state.homography.tolist() if state.homography is not None else None,
        ProjectKeys.REPROJECTION_AVG: state.reprojection_avg,
        ProjectKeys.REPROJECTION_MEDIAN: state.reprojection_median,
        ProjectKeys.REPROJECTION_MAX: state.reprojection_max,
        ProjectKeys.REPROJECTION_ERRORS: state.reprojection_errors,
        ProjectKeys.FLATTEN_ENABLED: bool(state.flattened_photo is not None),
        ProjectKeys.WORKFLOW_STAGE: state.workflow_stage,
        ProjectKeys.PHOTO_VIEW_ZOOM: state.photo_view_zoom,
        ProjectKeys.PHOTO_VIEW_PAN_X: state.photo_view_pan_x,
        ProjectKeys.PHOTO_VIEW_PAN_Y: state.photo_view_pan_y,
        ProjectKeys.PLAN_VIEW_ZOOM: state.plan_view_zoom,
        ProjectKeys.PLAN_VIEW_PAN_X: state.plan_view_pan_x,
        ProjectKeys.PLAN_VIEW_PAN_Y: state.plan_view_pan_y,
        ProjectKeys.POINT_EDITOR_STATE: {
            "selected_photo_point": state.selected_photo_point,
            "selected_plan_point": state.selected_plan_point,
            "selected_point_side": state.selected_point_side,
        },
        ProjectKeys.QUALITY_PROFILE: {
            "avg": state.quality_profile.average_error,
            "median": state.quality_profile.median_error,
            "max": state.quality_profile.max_error,
            "bad_count": state.quality_profile.bad_count,
            "grade": state.quality_profile.grade,
            "used_count": state.quality_profile.used_count,
            "score": state.quality_profile.score,
            "outlier_indices": state.quality_profile.outlier_indices,
        },
        ProjectKeys.QUALITY_GRADE: state.quality_profile.grade,
    }


def apply_project_dict_to_state(data: Dict[str, Any]) -> AppState:
    payload, _migration_messages = migrate_project_payload(data)
    state = AppState()

    state.photo_path = payload.get(ProjectKeys.PHOTO_PATH)
    state.plan_path = payload.get(ProjectKeys.PLAN_PATH)
    state.photo_points = parse_points(payload.get(ProjectKeys.PHOTO_POINTS))
    state.plan_points = parse_points(payload.get(ProjectKeys.PLAN_POINTS))
    state.alignment_mode = payload.get(ProjectKeys.ALIGNMENT_MODE, state.alignment_mode)
    state.flatten_preset = payload.get(ProjectKeys.FLATTEN_PRESET, state.flatten_preset)
    state.flatten_intensity = _coerce_int(payload.get(ProjectKeys.FLATTEN_INTENSITY), state.flatten_intensity)
    state.show_flat_photo = bool(payload.get(ProjectKeys.SHOW_FLAT_PHOTO, state.show_flat_photo))
    state.show_split_compare = bool(payload.get(ProjectKeys.SHOW_SPLIT_VIEW, state.show_split_compare))
    state.split_ratio = _coerce_float(payload.get(ProjectKeys.SPLIT_VIEW_RATIO), state.split_ratio)
    state.result_view_mode = payload.get(ProjectKeys.RESULT_VIEW_MODE, state.result_view_mode)
    state.overlay_alpha = _coerce_float(payload.get(ProjectKeys.OVERLAY_ALPHA), state.overlay_alpha)
    state.homography = parse_homography(payload.get(ProjectKeys.HOMOGRAPHY))
    state.reprojection_avg = payload.get(ProjectKeys.REPROJECTION_AVG)
    state.reprojection_median = payload.get(ProjectKeys.REPROJECTION_MEDIAN)
    state.reprojection_max = payload.get(ProjectKeys.REPROJECTION_MAX)
    state.reprojection_errors = [
        float(v)
        for v in payload.get(ProjectKeys.REPROJECTION_ERRORS, [])
        if isinstance(v, (int, float))
    ]
    state.photo_view_zoom = _coerce_float(payload.get(ProjectKeys.PHOTO_VIEW_ZOOM), state.photo_view_zoom)
    state.photo_view_pan_x = _coerce_int(payload.get(ProjectKeys.PHOTO_VIEW_PAN_X), state.photo_view_pan_x)
    state.photo_view_pan_y = _coerce_int(payload.get(ProjectKeys.PHOTO_VIEW_PAN_Y), state.photo_view_pan_y)
    state.plan_view_zoom = _coerce_float(payload.get(ProjectKeys.PLAN_VIEW_ZOOM), state.plan_view_zoom)
    state.plan_view_pan_x = _coerce_int(payload.get(ProjectKeys.PLAN_VIEW_PAN_X), state.plan_view_pan_x)
    state.plan_view_pan_y = _coerce_int(payload.get(ProjectKeys.PLAN_VIEW_PAN_Y), state.plan_view_pan_y)
    state.workflow_stage = payload.get(ProjectKeys.WORKFLOW_STAGE, "")

    editor_state = payload.get(ProjectKeys.POINT_EDITOR_STATE) if isinstance(payload.get(ProjectKeys.POINT_EDITOR_STATE), dict) else {}
    state.selected_photo_point = editor_state.get("selected_photo_point")
    state.selected_plan_point = editor_state.get("selected_plan_point")
    state.selected_point_side = editor_state.get("selected_point_side", state.selected_point_side)

    state.point_history = []
    state.point_redo = []
    state.push_point_history()

    state.quality_profile = parse_alignment_profile(payload.get(ProjectKeys.QUALITY_PROFILE))
    state.reprojection_avg = state.quality_profile.average_error
    state.outlier_indices = state.quality_profile.outlier_indices
    state.alignment_score = state.quality_profile.score

    return state
