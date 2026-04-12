from PySide6.QtCore import QObject, QRectF, Signal
from PySide6.QtGui import QColor, QFont, QPen
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsSimpleTextItem



class ROI(QObject):

    rect_changed = Signal()     # rect changed due to script
    rect_moved = Signal()       # rect moved by user

    def __init__(self, rect: QRectF, label: str = "", id: int = 0, color=QColor("#4fffb0")):
        super().__init__()
        self.rect: QRectF = rect
        self.label: str = label
        self.id: int = id
        self.color: QColor = color

    def change_rect(self, rect: QRectF):
        self.rect = rect
        self.rect_changed.emit()

    def move_rect(self, rect: QRectF):
        self.rect = rect
        self.rect_moved.emit()



class ROIManager(QObject):

    rect_changed = Signal()     # rect changed due to script
    rect_moved = Signal()       # rect moved by user

    def __init__(self):
        super().__init__()

        self.rois: dict[int, ROI] = {}
        self.next_id = 0
        self.free_ids = []


    def create_roi(self, rect: QRectF):
        roi = ROI(rect)
        roi.rect_moved.connect(self.rect_moved.emit)
        roi.rect_changed.connect(self.rect_changed.emit)
        self.add_roi(roi)
        self.rect_moved.emit()
        return roi

    def add_roi(self, roi: ROI) -> int:
        if not self.free_ids:
            roi_id = self.next_id
            self.next_id += 1
        else:
            roi_id = self.free_ids.pop(0)

        self.rois[roi_id] = roi
        roi.id = roi_id

        return roi_id


    def remove_roi(self, roi_id: int):
        self.rois.pop(roi_id)
        self.free_ids.append(roi_id)


# class ROI(QObject):
#     rect_changed = Signal()
#
#     def __init__(
#         self, rect: QRectF, label: str = "", id: int = 0, color=QColor("#4fffb0")
#     ) -> None:
#         super().__init__()
#         self.rect: QRectF = rect
#         self.label: str = label
#         self.id: int = id
#         self.color: QColor = color
#
#     def update_rect(self, x, y, w, h):
#         self.rect.setRect(x, y, w, h)
#         self.rect_changed.emit()


# class ROIManager(QObject):
#     rois_changed = Signal(bool)
#
#     def __init__(self):
#         super().__init__()
#         self.rois: dict[int, ROI] = {}
#         self.free_ids: list[int] = []
#         self.next_id: int = 0
#         self.rois_locked = False
#
#     def create_roi(self, rect: QRectF):
#         roi = ROI(rect)
#         self.add_roi(roi)
#         return roi
#
#     def add_roi(self, roi: ROI) -> int:
#         if not self.free_ids:
#             roi_id = self.next_id
#             self.next_id += 1
#         else:
#             roi_id = self.free_ids.pop(0)
#
#         self.rois[roi_id] = roi
#         roi.id = roi_id
#
#         self.rois_changed.emit(False)
#
#         return roi_id
#
#     def move_roi(self, new_rect: QRectF, roi_id):
#         if self.rois_locked:
#             return
#
#         self.rois[roi_id].update_rect(new_rect.x(), new_rect.y(), new_rect.width(),
#                                       new_rect.height())
#
#         self.rois_changed.emit(False)
#
#     def move_roi_no_signal(self, new_rect: QRectF, roi_id):
#         if self.rois_locked:
#             return
#
#         self.rois[roi_id].update_rect(new_rect.x(), new_rect.y(), new_rect.width(),
#                                       new_rect.height())
#
#
#     def remove_roi(self, roi_id: int):
#         self.rois.pop(roi_id)
#         self.free_ids.append(roi_id)
#
#         self.rois_changed.emit(False)
#
#     def lock_rois(self, lock: bool):
#         print("set roi lock to:", lock)
#         self.rois_locked = lock
#
#
# class ROIItem(QGraphicsRectItem):
#
#     def __init__(self, frame_rect: QRectF, roi_manager: ROIManager):
#         super().__init__()
#         self.roi = None
#         self.frame_rect = frame_rect
#         self._roi_manager = roi_manager
#
#         color = QColor("#4fffb0")
#
#         self._pen = QPen(color)
#         self._pen.setWidth(2)
#         self.setPen(self._pen)
#
#         self.label = QGraphicsSimpleTextItem(self)
#         self.label.setBrush(color)
#
#         # Use a monospace font for that "data" look
#         font = QFont("JetBrains Mono", 12)
#         font.setBold(True)
#         self.label.setFont(font)
#
#         self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable, True)
#         self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable, True)
#         self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
#
#     def create_roi(self):
#         self.roi = self._roi_manager.create_roi(self.rect())
#         self._pen.setColor(self.roi.color)
#
#         self.label.setPos(self.rect().x(), self.rect().y() - 18)
#         self.label.setBrush(self.roi.color)
#         self.label.setText(f"#{self.roi.id}")
#
#         self.roi.rect_changed.connect(self._on_rect_changed)
#
#     def delete_roi(self):
#         if self.roi is not None:
#             self._roi_manager.remove_roi(self.roi.id)
#
#     def _on_rect_changed(self):
#         if self.roi is None:
#             return
#         new_rect = self.roi.rect
#         self.setRect(new_rect)
#         self.label.setPos(self.rect().x(), self.rect().y() - 18)
#
#
#     def update_roi(self, rect):
#         if not self.roi is None:
#             self.roi.blockSignals(True)
#             self._roi_manager.move_roi(rect, self.roi.id)
#             self.roi.blockSignals(False)
#
#     def itemChange(self, change, value):
#         if (
#             change == QGraphicsRectItem.GraphicsItemChange.ItemPositionChange
#             and self.frame_rect is not None
#         ):
#             diff_vec = value
#
#             rect = self.rect()
#             x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
#             new_x = x + diff_vec.x()
#             new_y = y + diff_vec.y()
#
#             # Constrain horizontally
#             if new_x < self.frame_rect.left():
#                 diff_vec.setX(self.frame_rect.left() - x)
#             elif new_x + w > self.frame_rect.right():
#                 diff_vec.setX(self.frame_rect.right() - x - w)
#
#             # # Constrain vertically
#             if new_y < self.frame_rect.top():
#                 diff_vec.setY(self.frame_rect.top() - y)
#             elif new_y + h > self.frame_rect.bottom():
#                 diff_vec.setY(self.frame_rect.bottom() - y - h)
#
#             diff_vec.setX(round(diff_vec.x()))
#             diff_vec.setY(round(diff_vec.y()))
#
#             rect = self.mapToScene(self.rect()).boundingRect()
#             if self.roi is not None and not self._roi_manager.rois_locked:
#                 self.update_roi(rect)
#
#         return super().itemChange(change, value)
