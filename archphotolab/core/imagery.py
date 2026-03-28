from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np

from archphotolab.constants import (
    BACKGROUND_EPSILON,
    BACKGROUND_ESTIMATION_SCALE,
    CLAHE_CLIP_LIMIT,
    CLAHE_TILE,
    MSG_IMAGE_LOAD_FAIL_FMT,
    MSG_IMAGE_NOT_FOUND,
    MSG_IMAGE_RGB_ONLY,
    MSG_IMAGE_UNSUPPORTED_EXTENSION,
    MSG_OVERLAY_IMAGE_MISSING,
    MSG_OVERLAY_IMAGE_SIZE_MISMATCH,
    IMAGE_EXT_MAX,
    IMAGE_EXT_MIN,
    KERNEL_MIN_SIZE,
    SUPPORTED_IMAGE_EXTENSIONS,
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


def blend_overlay(
    photo_image: np.ndarray,
    warped_plan_image: np.ndarray,
    alpha: float,
) -> np.ndarray:
    """Blend two RGB images in photo coordinate space."""
    if photo_image is None or warped_plan_image is None:
        raise ValueError(MSG_OVERLAY_IMAGE_MISSING)
    if warped_plan_image.shape[:2] != photo_image.shape[:2]:
        raise ValueError(MSG_OVERLAY_IMAGE_SIZE_MISMATCH)

    alpha_clamped = float(np.clip(alpha, 0.0, 1.0))
    photo = photo_image.astype(np.float32)
    plan = warped_plan_image.astype(np.float32)

    result = photo * (1.0 - alpha_clamped) + plan * alpha_clamped
    return np.clip(result, 0, 255).astype(np.uint8)


def _safe_odd(value: int) -> int:
    value = max(KERNEL_MIN_SIZE, int(value))
    if value % 2 == 0:
        value += 1
    return value


def _background_kernel(size: Tuple[int, int]) -> int:
    h, w = size
    short = min(h, w)
    if short < 2:
        return KERNEL_MIN_SIZE
    # Large-kernel estimate of illumination: about 7~10% of short edge.
    k = max(31, int(short * BACKGROUND_ESTIMATION_SCALE))
    if k >= short:
        k = short - 1 if short % 2 else short - 2
    return _safe_odd(k)


def flatten_illumination(rgb_image: np.ndarray) -> np.ndarray:
    """Simple illumination flattening using background subtraction + CLAHE.

    목표:
    - 그림자/하이라이트로 인한 강한 명암 경향 완화
    - 기록용 판독성 향상
    """
    if rgb_image is None:
        raise ValueError(MSG_IMAGE_NOT_FOUND)

    if rgb_image.ndim != 3 or rgb_image.shape[2] != 3:
        raise ValueError(MSG_IMAGE_RGB_ONLY)

    rgb = rgb_image.astype(np.uint8)
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    l_float = l_channel.astype(np.float32)
    kernel = _background_kernel((rgb.shape[0], rgb.shape[1]))
    illum = cv2.GaussianBlur(l_float, (kernel, kernel), 0)

    mean_l = max(float(l_float.mean()), 1.0)
    reduced = l_float / (illum + BACKGROUND_EPSILON) * mean_l
    reduced = np.clip(reduced, IMAGE_EXT_MIN, IMAGE_EXT_MAX).astype(np.uint8)

    # Local contrast normalization for record-friendly flattening
    clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP_LIMIT, tileGridSize=CLAHE_TILE)
    reduced = clahe.apply(reduced)

    flat_lab = cv2.merge([reduced, a_channel, b_channel])
    return cv2.cvtColor(flat_lab, cv2.COLOR_LAB2RGB)
