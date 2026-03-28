from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from archphotolab.state import AppState


PROJECT_FORMAT = "0.1.0"


def state_to_dict(state: AppState) -> Dict[str, Any]:
    """Serialize app state to JSON payload."""
    return {
        "format_version": PROJECT_FORMAT,
        "photo_path": state.photo_path,
        "plan_path": state.plan_path,
        "photo_points": [{"x": float(x), "y": float(y)} for x, y in state.photo_points],
        "plan_points": [{"x": float(x), "y": float(y)} for x, y in state.plan_points],
        "overlay_alpha": float(state.overlay_alpha),
        "homography": state.homography.tolist() if state.homography is not None else None,
        "show_flat_photo": bool(state.show_flat_photo),
        "result_view_mode": state.result_view_mode,
        "reprojection_avg": state.reprojection_avg,
        "reprojection_max": state.reprojection_max,
        "reprojection_errors": state.reprojection_errors,
        "flatten_enabled": bool(state.flattened_photo is not None),
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
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError("프로젝트 파일 형식이 올바르지 않습니다.")
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
    state.photo_path = data.get("photo_path")
    state.plan_path = data.get("plan_path")
    state.photo_points = parse_points(data.get("photo_points"))
    state.plan_points = parse_points(data.get("plan_points"))
    state.overlay_alpha = float(data.get("overlay_alpha", state.overlay_alpha))
    state.homography = parse_homography(data.get("homography"))
    state.show_flat_photo = bool(data.get("show_flat_photo", state.show_flat_photo))
    state.result_view_mode = data.get("result_view_mode", state.result_view_mode)
    state.reprojection_avg = data.get("reprojection_avg")
    state.reprojection_max = data.get("reprojection_max")
    state.reprojection_errors = [
        float(v)
        for v in data.get("reprojection_errors", [])
        if isinstance(v, (int, float))
    ]
    return state
