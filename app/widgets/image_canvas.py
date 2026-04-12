import cv2
import numpy as np
from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QImage, QKeyEvent, QMouseEvent, QPixmap, QResizeEvent
from PySide6.QtWidgets import (
    QGraphicsItem,
    QGraphicsPixmapItem,
    QGraphicsScene,
    QGraphicsView,
    QSizePolicy,
)


class ImageCanvas(QGraphicsView):
    left_mouse_pressed = Signal(QMouseEvent)
    left_mouse_moved = Signal(QMouseEvent)
    left_mouse_released = Signal(QMouseEvent)
    delete_pressed = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.setMinimumSize(320, 240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._pixmap: QGraphicsPixmapItem | None = None

        self._graphics_scene = QGraphicsScene()
        self.setScene(self._graphics_scene)

        self._zoom_factor = 1.0
        self._panning = False
        self._left_mouse_is_pressed = False

    def add_item(self, item: QGraphicsItem):
        self._graphics_scene.addItem(item)

    def remove_item(self, item: QGraphicsItem):
        self._graphics_scene.removeItem(item)

    def set_pixmap(self, pixmap: QPixmap) -> None:
        if self._pixmap is None:
            self._pixmap = self._graphics_scene.addPixmap(pixmap)
        else:
            self._pixmap.setPixmap(pixmap)

        pw, ph = pixmap.width(), pixmap.height()
        self._graphics_scene.setSceneRect(0, 0, pw, ph)

    def set_image(self, image: np.ndarray) -> None:
        if image.ndim == 2:
            h, w = image.shape
            qimg = QImage(image.data, w, h, w, QImage.Format.Format_Grayscale8)
        else:
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb.shape
            qimg = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)

        self.set_pixmap(QPixmap.fromImage(qimg))

    def clear(self) -> None:
        self._pixmap = None
        self.update()

    def reset_view(self):
        self.resetTransform()
        self._zoom_factor = 1.0
        self.fit_in_view()

    def fit_in_view(self):
        if self._pixmap is None:
            return

        pw, ph = (
            self._pixmap.boundingRect().width(),
            self._pixmap.boundingRect().height(),
        )
        ww, wh = self.width(), self.height()

        factor = min(ww / pw, wh / ph)
        self.scale(factor, factor)

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

        if self._pixmap is not None and self._zoom_factor == 1:
            self.reset_view()

    def wheelEvent(self, event):
        zoom_in_factor = 1.15
        zoom_out_factor = 1 / zoom_in_factor

        if event.angleDelta().y() > 0:
            factor = zoom_in_factor
        else:
            factor = zoom_out_factor

        self._zoom_factor *= factor
        self.scale(factor, factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        elif event.button() == Qt.MouseButton.RightButton:
            self.reset_view()
        elif event.button() == Qt.MouseButton.LeftButton:
            self.left_mouse_pressed.emit(event)
            self._left_mouse_is_pressed = True

        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._left_mouse_is_pressed:
            self.left_mouse_moved.emit(event)

        if self._panning:
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
        return super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        elif event.button() == Qt.MouseButton.LeftButton:
            self._left_mouse_is_pressed = False
            self.left_mouse_released.emit(event)

        return super().mouseReleaseEvent(event)

    def keyPressEvent(self, event: QKeyEvent, /) -> None:
        if event.key() == Qt.Key.Key_Delete:
            self.delete_pressed.emit()
        return super().keyPressEvent(event)

    def get_items_at(self, pos: QPointF) -> list[QGraphicsItem]:
        return self._graphics_scene.items(pos)

    @property
    def pixmap(self):
        return self._pixmap
