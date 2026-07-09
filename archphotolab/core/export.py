from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image

from archphotolab.constants import (
    DEFAULT_TIMESTAMP_FORMAT,
    IMAGE_VALUE_MIN_INT,
    IMAGE_VALUE_MAX_INT,
    MSG_EXPORT_IMAGE_NOT_RGB,
    MSG_EXPORT_NO_IMAGE,
    PNG_FORMAT,
    PNG_NAME_TEMPLATES,
    RGB_CHANNELS_EXPECTED,
)


def default_export_name(kind: str, timestamp: str) -> str:
    template = PNG_NAME_TEMPLATES[kind]
    return template.format(timestamp=timestamp)


def now_timestamp() -> str:
    return datetime.now().strftime(DEFAULT_TIMESTAMP_FORMAT)


def get_unique_path(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return path
    parent = p.parent
    stem = p.stem
    suffix = p.suffix
    counter = 1
    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return str(new_path)
        counter += 1


def save_png(path: str, image: np.ndarray, overwrite: bool = False) -> str:
    if image is None:
        raise ValueError(MSG_EXPORT_NO_IMAGE)
    if image.ndim != 3 or image.shape[2] != RGB_CHANNELS_EXPECTED:
        raise ValueError(MSG_EXPORT_IMAGE_NOT_RGB)
    
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    
    final_path = path if overwrite else get_unique_path(path)
    
    img = np.clip(image, IMAGE_VALUE_MIN_INT, IMAGE_VALUE_MAX_INT).astype(np.uint8)
    Image.fromarray(img).save(final_path, format=PNG_FORMAT)
    return final_path


def export_paths(export_dir: str, timestamp: str | None = None) -> Tuple[str, str, str]:
    if timestamp is None:
        timestamp = now_timestamp()

    base = Path(export_dir)
    return (
        str(base / default_export_name("overlay", timestamp)),
        str(base / default_export_name("flat", timestamp)),
        str(base / default_export_name("warped", timestamp)),
    )
