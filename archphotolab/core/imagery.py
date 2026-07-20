from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np

from PIL import Image, ImageOps

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
    IMAGE_PROXY_MAX_DIM,
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
    try:
        with Image.open(path) as pil_img:
            pil_img = ImageOps.exif_transpose(pil_img)
            if pil_img.mode != "RGB":
                pil_img = pil_img.convert("RGB")
            return np.array(pil_img)
    except Exception as e:
        raise ValueError(MSG_IMAGE_LOAD_FAIL_FMT.format(path=path) + f" (Error: {e})")


def blend_overlay(photo_image: np.ndarray, warped_plan_image: np.ndarray, alpha: float) -> np.ndarray:
    """Blend two RGB/RGBA images in photo coordinate space (normal/opacity mode)."""
    if photo_image is None or warped_plan_image is None:
        raise ValueError(MSG_OVERLAY_IMAGE_MISSING)
    if warped_plan_image.shape[:2] != photo_image.shape[:2]:
        raise ValueError(MSG_OVERLAY_IMAGE_SIZE_MISMATCH)

    clamped_alpha = float(np.clip(alpha, 0.0, 1.0))
    photo = photo_image.astype(np.float32)
    
    # Handle RGBA plan input
    if warped_plan_image.shape[2] == 4:
        plan_rgb = warped_plan_image[:, :, :3].astype(np.float32)
        plan_alpha = (warped_plan_image[:, :, 3].astype(np.float32) / 255.0)[:, :, np.newaxis]
        effective_alpha = clamped_alpha * plan_alpha
        result = photo * (1.0 - effective_alpha) + plan_rgb * effective_alpha
    else:
        plan = warped_plan_image.astype(np.float32)
        result = photo * (1.0 - clamped_alpha) + plan * clamped_alpha
        
    return np.clip(result, IMAGE_VALUE_LOWER_CLIP, IMAGE_VALUE_UPPER_CLIP).astype(np.uint8)


def blend_multiply(
    photo_image: np.ndarray,
    warped_plan_image: np.ndarray,
    alpha: float,
    validity_mask: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Multiply blend: plan white background disappears, dark lines stay.

    Formula (inside valid region): result = photo * (plan / 255)
    Outside the warped plan boundary (border fill): photo is shown unchanged.

    validity_mask: uint8 grayscale from warp_validity_mask (255=valid, 0=border).
    If None, falls back to detecting the border fill as all-zero pixels.
    """
    if photo_image is None or warped_plan_image is None:
        raise ValueError(MSG_OVERLAY_IMAGE_MISSING)
    if warped_plan_image.shape[:2] != photo_image.shape[:2]:
        raise ValueError(MSG_OVERLAY_IMAGE_SIZE_MISMATCH)

    clamped_alpha = float(np.clip(alpha, 0.0, 1.0))
    photo = photo_image.astype(np.float32)
    
    # Check if plan has an alpha channel
    has_alpha = (warped_plan_image.shape[2] == 4)
    if has_alpha:
        plan_rgb = warped_plan_image[:, :, :3].astype(np.float32)
        plan_alpha = (warped_plan_image[:, :, 3].astype(np.float32) / 255.0)[:, :, np.newaxis]
    else:
        plan_rgb = warped_plan_image.astype(np.float32)
        plan_alpha = np.ones((warped_plan_image.shape[0], warped_plan_image.shape[1], 1), dtype=np.float32)

    # Build the validity weight map (0.0 = border/no-data, 1.0 = valid plan area)
    if validity_mask is not None:
        valid = (validity_mask.astype(np.float32) / 255.0)[:, :, np.newaxis]
    else:
        # Fallback: treat all-zero pixels as border fill (check RGB channels)
        valid = (plan_rgb.sum(axis=2) > 0).astype(np.float32)[:, :, np.newaxis]

    # Pure multiply result (only meaningful where valid)
    multiplied = photo * (plan_rgb / 255.0)

    # In valid areas: blend photo and multiplied result at effective alpha (including plan's alpha)
    # In border areas (valid=0): show photo unchanged regardless of alpha
    effective_alpha = clamped_alpha * valid * plan_alpha
    result = photo * (1.0 - effective_alpha) + multiplied * effective_alpha
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
    h, w = l_float.shape
    min_dim = min(h, w)
    target_min = 800
    if min_dim > target_min:
        scale_factor = target_min / min_dim
        new_w = int(w * scale_factor)
        new_h = int(h * scale_factor)
        l_down = cv2.resize(l_float, (new_w, new_h), interpolation=cv2.INTER_AREA)
        kernel = _background_kernel((new_h, new_w), params["kernel_scale"])
        illum_down = cv2.GaussianBlur(l_down, (kernel, kernel), 0)
        illum = cv2.resize(illum_down, (w, h), interpolation=cv2.INTER_LINEAR)
    else:
        kernel = _background_kernel((h, w), params["kernel_scale"])
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


def create_proxy_image(image: np.ndarray) -> Tuple[np.ndarray, float]:
    """Downsample image if it exceeds maximum proxy dimensions, returning (proxy_image, scale_ratio)."""
    if image is None:
        return None, 1.0
    h, w = image.shape[:2]
    max_dim = max(h, w)
    
    if max_dim <= IMAGE_PROXY_MAX_DIM:
        return image.copy(), 1.0
        
    scale = float(IMAGE_PROXY_MAX_DIM) / float(max_dim)
    new_w = int(round(w * scale))
    new_h = int(round(h * scale))
    
    proxy = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
    # recalculate actual scale based on exact integer dimensions
    actual_scale = float(new_w) / float(w)
    return proxy, actual_scale


def apply_color_keying(image: np.ndarray, target_rgb: Tuple[int, int, int], tolerance: int) -> np.ndarray:
    """Convert white/colored background pixels matching target_rgb within tolerance to transparent.
    
    Uses CIE L*a*b* color space for perceptual uniformity.
    Returns 4-channel RGBA numpy array.
    """
    if image is None:
        return None
        
    # Ensure we work in RGB first
    if image.shape[2] == 4:
        rgb = image[:, :, :3]
        alpha = image[:, :, 3].copy()
    else:
        rgb = image
        alpha = np.full((image.shape[0], image.shape[1]), 255, dtype=np.uint8)
        
    if target_rgb is None:
        # Default to (0,0) pixel color as target background key if none provided
        target_rgb = tuple(map(int, rgb[0, 0]))
        
    # Convert input RGB image to LAB space
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    
    # Convert target RGB color to LAB space
    target_pixel = np.array([[[target_rgb[0], target_rgb[1], target_rgb[2]]]], dtype=np.uint8)
    target_lab = cv2.cvtColor(target_pixel, cv2.COLOR_RGB2LAB)[0, 0]
    
    # Calculate Euclidean distance in LAB color space
    tr, tg, tb = target_lab
    diff = lab.astype(np.float32) - np.array([tr, tg, tb], dtype=np.float32)
    dist = np.sqrt(np.sum(diff ** 2, axis=2))
    
    # Tolerance scaling factor (since max tolerance is 100 and LAB max distance is ~442.0)
    # A tolerance value of 100 corresponds to full threshold of 442.0.
    scale_factor = 442.0 / 100.0
    mask = dist <= float(tolerance * scale_factor)
    alpha[mask] = 0
    
    # Merge back to RGBA
    rgba = cv2.merge([rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2], alpha])
    return rgba
