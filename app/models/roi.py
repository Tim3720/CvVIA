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

