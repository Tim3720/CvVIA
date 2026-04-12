from typing import Optional

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QScrollArea, QVBoxLayout, QWidget

from app.widgets.image_canvas import ImageCanvas


class ROICard(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 1. Set a specific object name for CSS targeting
        self.setObjectName("ROICard")
        # 2. Add some internal padding
        self.setContentsMargins(5, 5, 5, 5)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)  # Space between Label and Canvas

        self.label = QLabel("ROI Snapshot")
        # Apply the "heading" style from your stylesheet
        self.label.setProperty("heading", True)

        # This is your existing custom widget
        self.canvas = ImageCanvas()

        layout.addWidget(self.label)
        layout.addWidget(self.canvas)


class ROIOutput(QScrollArea):
    def __init__(self):
        super().__init__()
        self.setWidgetResizable(True)

        self._build_ui()

        self._roi_cards = []

        self._current_rois = 0

    def _build_ui(self):
        self.content_widget = QWidget()
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        self.grid_layout.setSpacing(15)

        self.setWidget(self.content_widget)

        self.columns = 1

    def update_rois(self, rois: list[tuple[Optional[np.ndarray], int]]):
        if len(rois) != self._current_rois:
            # clear grid:
            # while self.grid_layout.count():
            #     item = self.grid_layout.takeAt(0)
            #     widget = item.widget()
            #     if widget:
            #         widget.deleteLater()
            while self._roi_cards:
                card = self._roi_cards.pop()
                card.deleteLater()

            # fill grid:
            for i in range(len(rois)):
                row = i // self.columns
                col = i % self.columns

                card = ROICard()
                self._roi_cards.append(card)
                self.grid_layout.addWidget(card, row, col)
            self._current_rois = len(rois)

        for i, roi_pair in enumerate(rois):
            roi_card = self._roi_cards[i]
            roi, idx = roi_pair
            roi_card.label.setText(f"ROI {idx}")
            if roi is not None:
                roi_card.canvas.set_image(roi)
