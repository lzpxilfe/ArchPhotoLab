from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Tuple

import numpy as np
from PIL import Image


PNG_FILENAMES = {
    "overlay": "overlay_result_{timestamp}.png",
    "flat": "flat_photo_{timestamp}.png",
    "warped": "warped_plan_{timestamp}.png",
}


def default_export_name(kind: str, timestamp: str) -> str:
    template = PNG_FILENAMES[kind]
    return template.format(timestamp=timestamp)


def now_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_png(path: str, image: np.ndarray) -> None:
    if image is None:
        raise ValueError("저장할 이미지가 없습니다.")
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("RGB 이미지만 저장 가능합니다.")
    img = np.clip(image, 0, 255).astype(np.uint8)
    Image.fromarray(img).save(path, format="PNG")


def export_paths(export_dir: str, timestamp: str | None = None) -> Tuple[str, str, str]:
    if timestamp is None:
        timestamp = now_timestamp()

    base = Path(export_dir)
    return (
        str(base / default_export_name("overlay", timestamp)),
        str(base / default_export_name("flat", timestamp)),
        str(base / default_export_name("warped", timestamp)),
    )
