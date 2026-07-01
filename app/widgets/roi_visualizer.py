from typing import Optional

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QMouseEvent, QPen
from PySide6.QtWidgets import QGraphicsRectItem

from ..models.roi import ROI, ROIManager
from .image_canvas import ImageCanvas, Qt


class ROIItem(QGraphicsRectItem):

    def __init__(self, roi: Optional[ROI], frame_rect: QRectF):
        super().__init__()
        self.set_flags(False)
        self.frame_rect = frame_rect

        self.roi = roi
        if not self.roi is None:
            self.setRect(0, 0, self.roi.rect.width(), self.roi.rect.height())
            self.setPos(self.roi.rect.x(), self.roi.rect.y())
            self.roi.rect_changed.connect(self.on_rect_change)


        color = QColor("#4fffb0")

        self._pen = QPen(color)
        self._pen.setWidth(2)
        self.setPen(self._pen)
        self.flag_status = True

    def on_rect_change(self):
        if self.roi is None:
            return

        new_rect = self.roi.rect
        if new_rect == self.rect():
            return

        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsScenePositionChanges,
                     False)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges,
                     False)
        self.setRect(0, 0, new_rect.width(), new_rect.height())
        self.setPos(new_rect.x(), new_rect.y())
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsScenePositionChanges,
                     self.flag_status)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges,
                     self.flag_status)


    def set_flags(self, value: bool):
        self.flag_status = value
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, value)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, value)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges, value)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsScenePositionChanges, value)


    def itemChange(self, change, value):
        if (change == QGraphicsRectItem.GraphicsItemChange.ItemPositionChange and not
            self.roi is None):
    
            # compute new rect:
            diff_vec = value

            rect = self.rect()
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            new_x = x + diff_vec.x()
            new_y = y + diff_vec.y()

            # Constrain horizontally
            if new_x < self.frame_rect.left():
                diff_vec.setX(self.frame_rect.left() - x)
            elif new_x + w > self.frame_rect.right():
                diff_vec.setX(self.frame_rect.right() - x - w)

            # # Constrain vertically
            if new_y < self.frame_rect.top():
                diff_vec.setY(self.frame_rect.top() - y)
            elif new_y + h > self.frame_rect.bottom():
                diff_vec.setY(self.frame_rect.bottom() - y - h)

            diff_vec.setX(round(diff_vec.x()))
            diff_vec.setY(round(diff_vec.y()))

            rect = self.mapToScene(self.rect()).boundingRect()
            self.roi.move_rect(rect)

        return super().itemChange(change, value)





class ROIVisualizer:
    def __init__(self, canvas: ImageCanvas, roi_manager: ROIManager) -> None:
        self._canvas = canvas
        self._roi_manager = roi_manager
        self._drawing = False

        self._current_roi: Optional[ROIItem] = None
        self._roi_items: list[ROIItem] = []
        self._rois_locked: bool = False

        self._connect_signals()


    def _connect_signals(self):
        self._canvas.left_mouse_pressed.connect(self.on_mouse_press)
        self._canvas.left_mouse_moved.connect(self.on_mouse_move)
        self._canvas.left_mouse_released.connect(self.on_mouse_release)
        self._canvas.delete_pressed.connect(self.delete_selected_rois)


    def on_mouse_press(self, event: QMouseEvent):
        if self._canvas.pixmap is None or self._rois_locked:
            return
        scene_pos = self._canvas.mapToScene(event.pos())
        if scene_pos.x() < 0 or scene_pos.y() < 0:
            return

        items = self._canvas.get_items_at(scene_pos)
        for item in items:
            if isinstance(item, QGraphicsRectItem):
                return

        scene_pos = self._canvas.mapToScene(event.pos())
        self._drawing = True
        self._start_point = scene_pos

        self._start_point.setX(round(self._start_point.x()))
        self._start_point.setY(round(self._start_point.y()))

        frame_rect = self._canvas.pixmap.sceneBoundingRect()

        self._current_roi = ROIItem(None, frame_rect)
        # self._current_roi.setRect(frame_rect)

        # self._current_roi = ROIItem(frame_rect, self._roi_manager)
        self._canvas.add_item(self._current_roi)



    def on_mouse_move(self, event: QMouseEvent):
        if not self._drawing:
            return

        current_point = self._canvas.mapToScene(event.pos())
        if self._start_point is None or self._current_roi is None:
            return

        current_point.setX(round(current_point.x()))
        current_point.setY(round(current_point.y()))

        dx = int(round(current_point.x() - self._start_point.x()))
        dy = int(round(current_point.y() - self._start_point.y()))

        # If Ctrl pressed → enforce square
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            side = min(abs(dx), abs(dy))

            dx = side if dx >= 0 else -side
            dy = side if dy >= 0 else -side

            current_point = self._start_point + type(self._start_point)(dx, dy)

        rect = QRectF(self._start_point, current_point).normalized()
        self._current_roi.setRect(rect)



    def on_mouse_release(self, event):
        if not self._drawing:
            return

        self._drawing = False
        if self._current_roi is None:
            return

        if self._current_roi.rect().width() * self._current_roi.rect().height() < 20:
            self._canvas.remove_item(self._current_roi)
            self._current_roi = None
            return

        # self._current_roi.create_roi()
        # self._roi_items.append(self._current_roi)

        roi = self._roi_manager.create_roi(self._current_roi.rect())

        self._roi_items.append(ROIItem(roi, self._current_roi.frame_rect))
        self._canvas.add_item(self._roi_items[-1])
        self._roi_items[-1].set_flags(True)

        self._canvas.remove_item(self._current_roi)
        self._current_roi = None


    def delete_selected_rois(self):
        to_remove: list[ROIItem] = []
        for roi in self._roi_items:
            if roi.isSelected():
                to_remove.append(roi)

        for roi in to_remove:
            if not roi.roi is None:
                self._roi_manager.remove_roi(roi.roi.id)
            self._roi_items.remove(roi)
            self._canvas.remove_item(roi)


    def delete_all_rois(self):
        for roi in self._roi_items:
            if not roi.roi is None:
                self._roi_manager.remove_roi(roi.roi.id)
            self._canvas.remove_item(roi)

        self._roi_items.clear()

    def lock_rois(self, lock: bool):
        self._rois_locked = lock
        for roi_item in self._roi_items:
            roi_item.set_flags(not lock)

