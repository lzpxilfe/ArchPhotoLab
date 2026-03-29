from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np

from archphotolab.constants import (
    BACKGROUND_EPSILON,
    BACKGROUND_ESTIMATION_SCALE,
    BACKGROUND_KERNEL_MIN,
    CLAHE_TILE,
    FLATTEN_PRESET_RECORD,
    FLATTEN_PRESET_INTENSITY_DEFAULT,
    FLATTEN_PRESET_KEYS,
    FLATTEN_PRESETS,
    FLATTEN_PRESET_SHADOW,
    FLATTEN_PRESET_SOFT,
    IMAGE_COLOR_CHANNEL_INDEX,
    IMAGE_EXT_MAX,
    IMAGE_VALUE_COUNT,
    IMAGE_VALUE_LOWER_CLIP,
    IMAGE_VALUE_UPPER_CLIP,
    KERNEL_MIN_SIZE,
    MSG_FLATTEN_PRESET_INVALID,
    MSG_IMAGE_LOAD_FAIL_FMT,
    MSG_IMAGE_NOT_FOUND,
    MSG_IMAGE_RGB_ONLY,
    MSG_IMAGE_UNSUPPORTED_EXTENSION,
    MSG_OVERLAY_IMAGE_MISSING,
    MSG_OVERLAY_IMAGE_SIZE_MISMATCH,
    OVERLAY_ALPHA_MIN,
    OVERLAY_ALPHA_MAX,
    POINT_PANEL_EPSILON,
    SUPPORTED_IMAGE_EXTENSIONS,
    SPLIT_VIEW_DEFAULT_RATIO,
    SPLIT_VIEW_MAX_RATIO,
    SPLIT_VIEW_MIN_RATIO,
)


def is_supported_image(path: str) -> bool:
    return Path(path).suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS


def ensure_supported(path: str) -> None:
    if not is_supported_image(path):
        raise ValueError(MSG_IMAGE_UNSUPPORTED_EXTENSION)


def load_rgb_image(path: str) -> np.ndarray:
    ensure_supported(path)
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(MSG_IMAGE_LOAD_FAIL_FMT.format(path=path))
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def blend_overlay(photo_image: np.ndarray, warped_plan_image: np.ndarray, alpha: float) -> np.ndarray:
    """Blend two RGB images in photo coordinate space."""
    if photo_image is None or warped_plan_image is None:
        raise ValueError(MSG_OVERLAY_IMAGE_MISSING)
    if warped_plan_image.shape[:2] != photo_image.shape[:2]:
        raise ValueError(MSG_OVERLAY_IMAGE_SIZE_MISMATCH)

    clamped_alpha = float(np.clip(alpha, 0.0, 1.0))
    photo = photo_image.astype(np.float32)
    plan = warped_plan_image.astype(np.float32)

    result = photo * (1.0 - clamped_alpha) + plan * clamped_alpha
    return np.clip(result, IMAGE_VALUE_LOWER_CLIP, IMAGE_VALUE_UPPER_CLIP).astype(np.uint8)


def _safe_odd(value: int) -> int:
    value = max(KERNEL_MIN_SIZE, int(value))
    if value % 2 == 0:
        value += 1
    return value


def _background_kernel(size: Tuple[int, int], scale: float) -> int:
    h, w = size
    short = min(h, w)
    if short < 2:
        return KERNEL_MIN_SIZE
    k = max(BACKGROUND_KERNEL_MIN, int(short * scale))
    if k >= short:
        k = short - 1 if short % 2 else short - 2
    return _safe_odd(k)


def _apply_gamma_channel(channel: np.ndarray, gamma: float) -> np.ndarray:
    inv_gamma = 1.0 / max(gamma, POINT_PANEL_EPSILON)
    lut = np.array([
        ((i / IMAGE_EXT_MAX) ** inv_gamma) * IMAGE_EXT_MAX
        for i in range(IMAGE_VALUE_COUNT)
    ]).astype("uint8")
    return cv2.LUT(channel.astype(np.uint8), lut)


def flatten_illumination(
    rgb_image: np.ndarray,
    preset: str = FLATTEN_PRESET_RECORD,
    intensity: int = FLATTEN_PRESET_INTENSITY_DEFAULT,
) -> np.ndarray:
    """Simple illumination flattening using background estimation + CLAHE.

    intensity: 0~100, where 0 is original and 100 is flattened result.
    """
    if rgb_image is None:
        raise ValueError(MSG_IMAGE_NOT_FOUND)

    if rgb_image.ndim != 3 or rgb_image.shape[2] != IMAGE_COLOR_CHANNEL_INDEX + 1:
        raise ValueError(MSG_IMAGE_RGB_ONLY)

    if preset not in FLATTEN_PRESET_KEYS:
        raise ValueError(MSG_FLATTEN_PRESET_INVALID)

    alpha = float(np.clip(int(intensity), OVERLAY_ALPHA_MIN, OVERLAY_ALPHA_MAX)) / float(OVERLAY_ALPHA_MAX)
    if alpha <= 0.0:
        return rgb_image.copy()

    params = FLATTEN_PRESETS[preset]
    rgb = rgb_image.astype(np.uint8)
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    l_float = l_channel.astype(np.float32)
    kernel = _background_kernel((rgb.shape[0], rgb.shape[1]), params["kernel_scale"])
    illum = cv2.GaussianBlur(l_float, (kernel, kernel), 0)

    mean_l = max(float(l_float.mean()), 1.0)
    reduced = l_float / (illum + BACKGROUND_EPSILON) * mean_l
    reduced = np.clip(reduced, IMAGE_VALUE_LOWER_CLIP, IMAGE_VALUE_UPPER_CLIP).astype(np.uint8)

    clahe = cv2.createCLAHE(clipLimit=float(params["clahe_clip"]), tileGridSize=CLAHE_TILE)
    reduced = clahe.apply(reduced)
    reduced = _apply_gamma_channel(reduced, float(params["gamma"]))

    flat_lab = cv2.merge([reduced, a_channel, b_channel])
    flat_rgb = cv2.cvtColor(flat_lab, cv2.COLOR_LAB2RGB)
    blended = cv2.addWeighted(rgb, 1.0 - alpha, flat_rgb, alpha, 0.0)
    return blended.astype(np.uint8)


def make_split_compare_image(
    original: np.ndarray,
    processed: np.ndarray,
    ratio: float = SPLIT_VIEW_DEFAULT_RATIO,
) -> np.ndarray:
    """Return side-by-side split image for before/after compare."""
    if original is None or processed is None:
        raise ValueError(MSG_IMAGE_NOT_FOUND)
    if original.shape != processed.shape:
        raise ValueError(MSG_OVERLAY_IMAGE_SIZE_MISMATCH)

    ratio = float(np.clip(ratio, SPLIT_VIEW_MIN_RATIO, SPLIT_VIEW_MAX_RATIO))
    width = original.shape[1]
    split = int(width * ratio)
    if split <= 0 or split >= width:
        return original.copy()

    left = original[:, :split]
    right = processed[:, split:]
    out = np.concatenate([left, right], axis=1)
    return out.astype(np.uint8)
