from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def is_supported_image(path: str) -> bool:
    return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS


def ensure_supported(path: str) -> None:
    if not is_supported_image(path):
        raise ValueError("PNG/JPG 파일만 지원됩니다.")


def load_rgb_image(path: str) -> np.ndarray:
    ensure_supported(path)
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"이미지를 불러올 수 없습니다: {path}")
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


def blend_overlay(
    photo_image: np.ndarray,
    warped_plan_image: np.ndarray,
    alpha: float,
) -> np.ndarray:
    """Blend two RGB images in photo coordinate space."""
    if photo_image is None or warped_plan_image is None:
        raise ValueError("overlay를 만들기 위한 이미지가 없습니다.")
    if warped_plan_image.shape[:2] != photo_image.shape[:2]:
        raise ValueError("overlay 이미지 크기가 다릅니다.")

    alpha_clamped = float(np.clip(alpha, 0.0, 1.0))
    photo = photo_image.astype(np.float32)
    plan = warped_plan_image.astype(np.float32)

    result = photo * (1.0 - alpha_clamped) + plan * alpha_clamped
    return np.clip(result, 0, 255).astype(np.uint8)


def _safe_odd(value: int) -> int:
    value = max(11, int(value))
    if value % 2 == 0:
        value += 1
    return value


def _background_kernel(size: Tuple[int, int]) -> int:
    h, w = size
    short = min(h, w)
    if short < 2:
        return 11
    # Large-kernel estimate of illumination: about 7~10% of short edge.
    k = max(31, int(short * 0.10))
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
        raise ValueError("평탄화할 이미지가 없습니다.")

    if rgb_image.ndim != 3 or rgb_image.shape[2] != 3:
        raise ValueError("RGB 이미지만 지원됩니다.")

    rgb = rgb_image.astype(np.uint8)
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    l_float = l_channel.astype(np.float32)
    kernel = _background_kernel((rgb.shape[0], rgb.shape[1]))
    illum = cv2.GaussianBlur(l_float, (kernel, kernel), 0)

    mean_l = max(float(l_float.mean()), 1.0)
    reduced = l_float / (illum + 1e-6) * mean_l
    reduced = np.clip(reduced, 0, 255).astype(np.uint8)

    # Local contrast normalization for record-friendly flattening
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    reduced = clahe.apply(reduced)

    flat_lab = cv2.merge([reduced, a_channel, b_channel])
    return cv2.cvtColor(flat_lab, cv2.COLOR_LAB2RGB)
