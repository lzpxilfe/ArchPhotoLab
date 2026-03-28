from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from archphotolab.constants import APP_VERSION, JSON_CHARSET_ENCODING, ProjectKeys
from archphotolab.constants import MSG_PROJECT_FORMAT_INVALID
from archphotolab.state import AppState


PROJECT_FORMAT = APP_VERSION


def state_to_dict(state: AppState) -> Dict[str, Any]:
    """Serialize app state to JSON payload."""
    return {
        ProjectKeys.FORMAT_VERSION: PROJECT_FORMAT,
        ProjectKeys.PHOTO_PATH: state.photo_path,
        ProjectKeys.PLAN_PATH: state.plan_path,
        ProjectKeys.PHOTO_POINTS: [{"x": float(x), "y": float(y)} for x, y in state.photo_points],
        ProjectKeys.PLAN_POINTS: [{"x": float(x), "y": float(y)} for x, y in state.plan_points],
        ProjectKeys.OVERLAY_ALPHA: float(state.overlay_alpha),
        ProjectKeys.HOMOGRAPHY: state.homography.tolist() if state.homography is not None else None,
        ProjectKeys.SHOW_FLAT_PHOTO: bool(state.show_flat_photo),
        ProjectKeys.RESULT_VIEW_MODE: state.result_view_mode,
        ProjectKeys.REPROJECTION_AVG: state.reprojection_avg,
        ProjectKeys.REPROJECTION_MAX: state.reprojection_max,
        ProjectKeys.REPROJECTION_ERRORS: state.reprojection_errors,
        ProjectKeys.FLATTEN_ENABLED: bool(state.flattened_photo is not None),
    }


def parse_homography(value: Any):
    if value is None or not isinstance(value, list) or len(value) != 3:
        return None
    import numpy as np

    try:
        arr = np.array(value, dtype=float)
    except Exception:
        return None
    if arr.shape != (3, 3):
        return None
    return arr


def parse_points(value: Any) -> List[Tuple[float, float]]:
    points: List[Tuple[float, float]] = []
    if not isinstance(value, list):
        return points

    for item in value:
        if isinstance(item, dict) and "x" in item and "y" in item:
            points.append((float(item["x"]), float(item["y"])))
    return points


def load_project(path: str) -> Dict[str, Any]:
    """Load raw project dictionary from JSON."""
    with open(path, "r", encoding=JSON_CHARSET_ENCODING) as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(MSG_PROJECT_FORMAT_INVALID)
    return data


def resolve_saved_image_path(
    saved_path: Optional[str],
    project_file: str,
    fallback_dirs: Optional[List[str]] = None,
) -> Optional[str]:
    """Resolve saved absolute/relative paths with fallback search."""
    if not saved_path:
        return None

    if fallback_dirs is None:
        fallback_dirs = []

    project_dir = Path(project_file).resolve().parent
    filename = Path(saved_path).name

    candidates = []
    if os.path.isabs(saved_path):
        candidates.append(saved_path)
    else:
        candidates.append(str((project_dir / saved_path)))

    candidates.append(str(Path(saved_path).expanduser()))
    candidates.append(str((Path.home() / filename)))

    search_dirs = [str(project_dir), os.getcwd(), *fallback_dirs]
    for d in search_dirs:
        if d:
            candidates.append(str(Path(d).expanduser() / filename))

    for candidate in candidates:
        if candidate and os.path.exists(candidate):
            return os.path.abspath(candidate)

    return None


def apply_project_dict_to_state(data: Dict[str, Any]) -> AppState:
    """Convert project payload to state object."""
    state = AppState()
    state.photo_path = data.get(ProjectKeys.PHOTO_PATH)
    state.plan_path = data.get(ProjectKeys.PLAN_PATH)
    state.photo_points = parse_points(data.get(ProjectKeys.PHOTO_POINTS))
    state.plan_points = parse_points(data.get(ProjectKeys.PLAN_POINTS))
    state.overlay_alpha = float(data.get(ProjectKeys.OVERLAY_ALPHA, state.overlay_alpha))
    state.homography = parse_homography(data.get(ProjectKeys.HOMOGRAPHY))
    state.show_flat_photo = bool(data.get(ProjectKeys.SHOW_FLAT_PHOTO, state.show_flat_photo))
    state.result_view_mode = data.get(ProjectKeys.RESULT_VIEW_MODE, state.result_view_mode)
    state.reprojection_avg = data.get(ProjectKeys.REPROJECTION_AVG)
    state.reprojection_max = data.get(ProjectKeys.REPROJECTION_MAX)
    state.reprojection_errors = [
        float(v)
        for v in data.get(ProjectKeys.REPROJECTION_ERRORS, [])
        if isinstance(v, (int, float))
    ]
    return state
