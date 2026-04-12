from typing import Optional

from PySide6.QtWidgets import QVBoxLayout, QWidget

from ..models.image_source import Frame
from .image_canvas import ImageCanvas


class FrameOutput(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self._canvas = ImageCanvas(self)

        layout.addWidget(self._canvas)

    def show_output(self, frame: Optional[Frame]):
        if frame is not None:
            self._canvas.set_image(frame.frame)

    def _connect_signals(self): ...
