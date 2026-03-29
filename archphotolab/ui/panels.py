from __future__ import annotations

from typing import Optional, Sequence

import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QWidget

from archphotolab.constants import (
    ERROR_GRADE_WARNING,
    MIN_PANEL_SIZE,
    IMAGE_COLOR_CHANNEL_INDEX,
    IMAGE_PANEL_BACKGROUND_RGB,
    IMAGE_PANEL_BORDER_RGB,
    IMAGE_PANEL_HINT_TEXT,
    IMAGE_PANEL_HINT_TEXT_RGB,
    IMAGE_PANEL_HINT_X,
    IMAGE_PANEL_TEXT_RGB,
    IMAGE_PANEL_TITLE_BAR_RGB,
    IMAGE_PANEL_TITLE_X,
    IMAGE_PANEL_TITLE_Y_OFFSET,
    PANEL_RENDER_PADDING_BOTTOM,
    PANEL_TOP_BANNER_HEIGHT,
    POINT_PANEL_HINT_FONT_SIZE,
    POINT_PANEL_MOUSE_DRAG_ROUNDING,
    POINT_PANEL_WHEEL_ANGLE_DIVISOR,
    POINT_PANEL_WHEEL_ZOOM_IN,
    POINT_PANEL_WHEEL_ZOOM_OUT,
    POINT_PANEL_ZOOM_DEFAULT,
    POINT_PANEL_ZOOM_EPSILON,
    POINT_PANEL_ZOOM_MAX,
    POINT_PANEL_ZOOM_MIN,
    POINT_PANEL_INITIAL_BASE_SCALE,
    POINT_BLEND_COLOR_MIN,
    POINT_BLEND_COLOR_MAX,
    POINT_BLEND_MIDPOINT,
    POINT_PANEL_COLOR_CHANNELS,
    POINT_ERROR_HIGH_RGB,
    POINT_ERROR_LOW_RGB,
    POINT_ERROR_MID_RGB,
    POINT_HOVER_RADIUS_FALLBACK_SCALE,
    POINT_HOVER_RADIUS_MAX,
    POINT_HOVER_RADIUS_MIN,
    POINT_HOVER_RADIUS_SCALE,
    POINT_LABEL_FONT_SIZE,
    POINT_LABEL_OFFSET_X,
    POINT_LABEL_OFFSET_Y,
    POINT_LABEL_TEXT_RGB,
    POINT_MARK_SIZE,
    POINT_NORMAL_RGB,
    POINT_OUTLINE_RGB,
    POINT_SELECTED_RGB,
    POINT_WARNING_RGB,
    UI_FONT_FAMILY,
    UI_TITLE_FONT_SIZE,
    UI_TITLE_OFFSET_Y,
    )
from archphotolab.constants import MSG_IMAGE_RGB_ONLY


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


class ImagePanel(QWidget):
    pointAdded = Signal(float, float)
    pointMoveStarted = Signal(int, float, float)
    pointMoved = Signal(int, float, float)
    pointMoveFinished = Signal(int, float, float)
    pointRemoved = Signal(int)
    pointSelected = Signal(int)
    viewStateChanged = Signal(float, int, int)

    def __init__(self, title: str, editable: bool = True, parent=None) -> None:
        super().__init__(parent)
        self._title = title
        self._editable = editable
        self._pixmap: Optional[QPixmap] = None
        self._image_width = 1
        self._image_height = 1

        self._points: list[tuple[float, float]] = []
        self._point_errors: list[float] = []
        self._warning_indices: set[int] = set()
        self._selected_index: Optional[int] = None
        self._paired_index: Optional[int] = None

        self._dragging_index: Optional[int] = None
        self._panning = False
        self._pan_last = (0.0, 0.0)

        self._base_scale = POINT_PANEL_INITIAL_BASE_SCALE
        self._zoom = POINT_PANEL_ZOOM_DEFAULT
        self._min_zoom = POINT_PANEL_ZOOM_MIN
        self._max_zoom = POINT_PANEL_ZOOM_MAX
        self._display_scale = POINT_PANEL_INITIAL_BASE_SCALE

        self._img_left = 0
        self._img_top = 0
        self._img_width = 1
        self._img_height = 1
        self._pan_offset_x = 0
        self._pan_offset_y = 0

        self.setMinimumSize(*MIN_PANEL_SIZE)
        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)

    def set_title(self, title: str) -> None:
        self._title = title
        self.update()

    def set_image(self, image: Optional[np.ndarray]) -> None:
        if image is None:
            self._pixmap = None
            self._image_width = 1
            self._image_height = 1
            self._img_width = 1
            self._img_height = 1
            self.update()
            return

        if image.ndim != POINT_PANEL_COLOR_CHANNELS or image.shape[2] != IMAGE_COLOR_CHANNEL_INDEX + 1:
            raise ValueError(MSG_IMAGE_RGB_ONLY)

        qimg = QImage(
            image.data,
            image.shape[1],
            image.shape[0],
            image.strides[0],
            QImage.Format_RGB888,
        ).copy()
        self._pixmap = QPixmap.fromImage(qimg)
        self._image_width = int(image.shape[1])
        self._image_height = int(image.shape[0])
        self._img_width = self._image_width
        self._img_height = self._image_height
        self._update_draw_geometry()
        self.update()

    def set_points(
        self,
        points: Sequence[tuple[float, float]],
        point_errors: Optional[Sequence[float]] = None,
        warning_indices: Optional[set[int]] = None,
        selected_index: Optional[int] = None,
        paired_index: Optional[int] = None,
    ) -> None:
        self._points = list(points)
        self._point_errors = [float(v) for v in (point_errors or []) if isinstance(v, (int, float))]
        self._warning_indices = set(warning_indices or [])
        self._selected_index = selected_index
        self._paired_index = paired_index
        self.update()

    def set_editable(self, enabled: bool) -> None:
        self._editable = enabled

    def set_view_state(self, zoom: float, pan_x: int, pan_y: int) -> None:
        self._zoom = _clamp(float(zoom), self._min_zoom, self._max_zoom)
        self._pan_offset_x = int(pan_x)
        self._pan_offset_y = int(pan_y)
        self._update_draw_geometry()
        self.update()
        self.viewStateChanged.emit(self._zoom, self._pan_offset_x, self._pan_offset_y)

    def get_view_state(self) -> tuple[float, int, int]:
        return self._zoom, self._pan_offset_x, self._pan_offset_y

    def reset_view_state(self) -> None:
        self._zoom = POINT_PANEL_ZOOM_DEFAULT
        self._pan_offset_x = 0
        self._pan_offset_y = 0
        self._update_draw_geometry()
        self.update()

    def _scaled_pixmap(self) -> Optional[QPixmap]:
        if self._pixmap is None:
            return None
        target_h = max(1, self.height() - PANEL_RENDER_PADDING_BOTTOM)
        return self._pixmap.scaled(
            self.width(),
            target_h,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

    def _update_draw_geometry(self) -> None:
        if self._pixmap is None:
            self._display_scale = max(
                POINT_PANEL_INITIAL_BASE_SCALE,
                POINT_PANEL_ZOOM_EPSILON,
            )
            self._base_scale = POINT_PANEL_INITIAL_BASE_SCALE
            self._img_left = 0
            self._img_top = 0
            self._img_width = max(1, self._image_width)
            self._img_height = max(1, self._image_height)
            return

        pix = self._scaled_pixmap()
        if pix is None:
            return
        target_h = max(1, self.height() - PANEL_RENDER_PADDING_BOTTOM)
        target_w = self.width()

        self._base_scale = pix.width() / max(self._image_width, 1)
        self._display_scale = max(self._base_scale * self._zoom, POINT_PANEL_ZOOM_EPSILON)
        base_left = (target_w - pix.width()) // 2
        base_top = PANEL_TOP_BANNER_HEIGHT + (target_h - pix.height()) // 2

        self._img_left = int(base_left + self._pan_offset_x)
        self._img_top = int(base_top + self._pan_offset_y)
        self._img_width = max(1, pix.width())
        self._img_height = max(1, pix.height())
        self.viewStateChanged.emit(self._zoom, self._pan_offset_x, self._pan_offset_y)

    def _to_widget_from_image(self, point: tuple[float, float]) -> Optional[tuple[int, int]]:
        if self._pixmap is None:
            return None
        return (
            self._img_left + int(round(point[0] * self._display_scale)),
            self._img_top + int(round(point[1] * self._display_scale)),
        )

    def _from_widget_to_image(self, x: float, y: float) -> Optional[tuple[float, float]]:
        if self._pixmap is None:
            return None
        img_x = (x - self._img_left) / self._display_scale
        img_y = (y - self._img_top) / self._display_scale
        if img_x < 0 or img_y < 0 or img_x > self._image_width or img_y > self._image_height:
            return None
        return float(img_x), float(img_y)

    def _find_point_at(self, widget_x: float, widget_y: float) -> Optional[int]:
        if self._pixmap is None or self._from_widget_to_image(widget_x, widget_y) is None:
            return None

        radius = max(
            POINT_HOVER_RADIUS_MIN,
            POINT_HOVER_RADIUS_SCALE / max(self._display_scale, POINT_HOVER_RADIUS_FALLBACK_SCALE),
        )
        radius = min(radius, POINT_HOVER_RADIUS_MAX)
        wx = widget_x - self._img_left
        wy = widget_y - self._img_top

        for idx, (x, y) in enumerate(self._points):
            sx = x * self._display_scale
            sy = y * self._display_scale
            if (sx - wx) ** 2 + (sy - wy) ** 2 <= radius ** 2:
                return idx
        return None

    def _error_color(self, error: float, max_error: float) -> tuple[int, int, int]:
        if max_error <= 0:
            return POINT_ERROR_LOW_RGB
        if error <= ERROR_GRADE_WARNING:
            return POINT_ERROR_LOW_RGB
        ratio = (error - ERROR_GRADE_WARNING) / max(max_error, ERROR_GRADE_WARNING)
        if ratio <= POINT_BLEND_MIDPOINT:
            return self._blend_color(POINT_ERROR_LOW_RGB, POINT_ERROR_MID_RGB, ratio / POINT_BLEND_MIDPOINT)
        return self._blend_color(POINT_ERROR_MID_RGB, POINT_ERROR_HIGH_RGB, (ratio - POINT_BLEND_MIDPOINT) / POINT_BLEND_MIDPOINT)

    @staticmethod
    def _blend_color(low: tuple[int, int, int], high: tuple[int, int, int], ratio: float) -> tuple[int, int, int]:
        r = max(POINT_BLEND_COLOR_MIN, min(POINT_BLEND_COLOR_MAX, int(low[0] + (high[0] - low[0]) * ratio)))
        g = max(POINT_BLEND_COLOR_MIN, min(POINT_BLEND_COLOR_MAX, int(low[1] + (high[1] - low[1]) * ratio)))
        b = max(POINT_BLEND_COLOR_MIN, min(POINT_BLEND_COLOR_MAX, int(low[2] + (high[2] - low[2]) * ratio)))
        return r, g, b

    def wheelEvent(self, event) -> None:
        if self._pixmap is None:
            return
        angle = event.angleDelta().y() / POINT_PANEL_WHEEL_ANGLE_DIVISOR
        if angle == 0:
            return

        factor = POINT_PANEL_WHEEL_ZOOM_IN if angle > 0 else POINT_PANEL_WHEEL_ZOOM_OUT
        before_zoom = self._zoom
        after_zoom = _clamp(self._zoom * factor, self._min_zoom, self._max_zoom)
        if abs(after_zoom - before_zoom) < POINT_PANEL_ZOOM_EPSILON:
            return

        cursor_x = event.position().x()
        cursor_y = event.position().y()

        pix = self._scaled_pixmap()
        if pix is None:
            return
        base_scale = pix.width() / max(self._image_width, 1)

        before_scale = self._display_scale
        img_x = (cursor_x - self._img_left) / max(before_scale, POINT_PANEL_ZOOM_EPSILON)
        img_y = (cursor_y - self._img_top) / max(before_scale, POINT_PANEL_ZOOM_EPSILON)

        self._zoom = after_zoom
        self._display_scale = base_scale * self._zoom
        target_w = self.width()
        target_h = max(1, self.height() - PANEL_RENDER_PADDING_BOTTOM)
        centered_left = (target_w - int(self._image_width * self._display_scale)) // 2
        centered_top = PANEL_TOP_BANNER_HEIGHT + (target_h - int(self._image_height * self._display_scale)) // 2
        self._img_left = int(cursor_x - img_x * self._display_scale)
        self._img_top = int(cursor_y - img_y * self._display_scale)
        self._pan_offset_x = self._img_left - centered_left
        self._pan_offset_y = self._img_top - centered_top
        self._update_draw_geometry()
        self.update()

    def _begin_pan(self, x: float, y: float) -> None:
        self._panning = True
        self._pan_last = (x, y)

    def _pan(self, x: float, y: float) -> bool:
        if not self._panning:
            return False
        dx = x - self._pan_last[0]
        dy = y - self._pan_last[1]
        self._pan_offset_x += int(round(dx, ndigits=POINT_PANEL_MOUSE_DRAG_ROUNDING))
        self._pan_offset_y += int(round(dy, ndigits=POINT_PANEL_MOUSE_DRAG_ROUNDING))
        self._pan_last = (x, y)
        self._update_draw_geometry()
        self.update()
        return True

    def mousePressEvent(self, event) -> None:
        if not self._editable or self._pixmap is None:
            return
        if event.button() in (Qt.RightButton, Qt.MiddleButton):
            self._begin_pan(event.position().x(), event.position().y())
            event.accept()
            return

        idx = self._find_point_at(event.position().x(), event.position().y())
        if event.button() == Qt.LeftButton:
            if idx is None:
                point = self._from_widget_to_image(event.position().x(), event.position().y())
                if point is not None:
                    self.pointAdded.emit(point[0], point[1])
            else:
                self._selected_index = idx
                self._dragging_index = idx
                point = self._from_widget_to_image(event.position().x(), event.position().y())
                if point is not None:
                    self.pointMoveStarted.emit(idx, point[0], point[1])
                self.pointSelected.emit(idx)
                self.update()

    def mouseMoveEvent(self, event) -> None:
        if event.buttons() & (Qt.RightButton | Qt.MiddleButton):
            self._pan(event.position().x(), event.position().y())
            return

        if not self._editable or self._pixmap is None or self._dragging_index is None:
            return
        if not event.buttons() & Qt.LeftButton:
            return

        point = self._from_widget_to_image(event.position().x(), event.position().y())
        if point is not None:
            self.pointMoved.emit(self._dragging_index, point[0], point[1])
        self.update()

    def mouseReleaseEvent(self, event) -> None:
        if self._dragging_index is not None and event.button() == Qt.LeftButton:
            point = self._from_widget_to_image(event.position().x(), event.position().y())
            if point is not None:
                self.pointMoveFinished.emit(self._dragging_index, point[0], point[1])

        self._dragging_index = None
        self._panning = False
        event.accept()

    def mouseDoubleClickEvent(self, event) -> None:
        if not self._editable or self._pixmap is None:
            return
        if event.button() == Qt.LeftButton:
            idx = self._find_point_at(event.position().x(), event.position().y())
            if idx is not None:
                self.pointRemoved.emit(idx)
                self._dragging_index = None
                self._selected_index = None

    def resizeEvent(self, event) -> None:
        self._update_draw_geometry()
        super().resizeEvent(event)

    def paintEvent(self, event) -> None:  # noqa: ARG002
        del event
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(*IMAGE_PANEL_BACKGROUND_RGB))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(QColor(*IMAGE_PANEL_BORDER_RGB), 1))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        painter.fillRect(0, 0, self.width(), PANEL_TOP_BANNER_HEIGHT, QColor(*IMAGE_PANEL_TITLE_BAR_RGB))

        title_font = QFont(UI_FONT_FAMILY)
        title_font.setPointSize(UI_TITLE_FONT_SIZE)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.setPen(QColor(*IMAGE_PANEL_TEXT_RGB))
        painter.drawText(IMAGE_PANEL_TITLE_X, UI_TITLE_FONT_SIZE + UI_TITLE_OFFSET_Y, self._title)

        if self._pixmap is None:
            painter.setPen(QColor(*IMAGE_PANEL_HINT_TEXT_RGB))
            painter.setFont(QFont(UI_FONT_FAMILY, POINT_PANEL_HINT_FONT_SIZE))
            painter.drawText(IMAGE_PANEL_HINT_X, self.height() // 2, IMAGE_PANEL_HINT_TEXT)
            return

        pix = self._scaled_pixmap()
        if pix is None:
            return
        target_w = self.width()
        target_h = max(1, self.height() - PANEL_RENDER_PADDING_BOTTOM)
        centered_left = (target_w - pix.width()) // 2
        centered_top = PANEL_TOP_BANNER_HEIGHT + (target_h - pix.height()) // 2
        self._img_left = int(centered_left + self._pan_offset_x)
        self._img_top = int(centered_top + self._pan_offset_y)

        self._base_scale = pix.width() / max(self._image_width, 1)
        self._display_scale = self._base_scale * self._zoom

        painter.drawPixmap(self._img_left, self._img_top, pix)

        warnings = set(self._warning_indices)
        max_error = max(self._point_errors) if self._point_errors else 0.0
        for idx, point in enumerate(self._points):
            widget_point = self._to_widget_from_image(point)
            if widget_point is None:
                continue

            px, py = widget_point
            if idx == self._selected_index or idx == self._paired_index:
                color = POINT_SELECTED_RGB
            elif idx in warnings:
                color = POINT_WARNING_RGB
            elif idx < len(self._point_errors):
                color = self._error_color(self._point_errors[idx], max_error)
            else:
                color = POINT_NORMAL_RGB

            painter.setPen(QPen(QColor(*POINT_OUTLINE_RGB), 1))
            painter.setBrush(QColor(*color))
            painter.drawEllipse(
                px - POINT_MARK_SIZE,
                py - POINT_MARK_SIZE,
                POINT_MARK_SIZE * 2,
                POINT_MARK_SIZE * 2,
            )
            painter.setPen(QColor(*POINT_LABEL_TEXT_RGB))
            painter.setFont(QFont(UI_FONT_FAMILY, POINT_LABEL_FONT_SIZE))
            painter.drawText(px + POINT_LABEL_OFFSET_X, py + POINT_LABEL_OFFSET_Y, str(idx + 1))
