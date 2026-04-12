from time import perf_counter
from typing import Optional

from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ..models.image_source import Frame, ImageSource, SourceInfo
from ..models.roi import ROIManager
from .image_canvas import ImageCanvas
from .roi_visualizer import ROIVisualizer


class SourceView(QWidget):


    lock_rois = Signal(bool)

    def __init__(
        self,
        image_source: ImageSource,
        roi_manager: ROIManager,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self._current_frame: int = 0
        self._playing: bool = False
        self._image_source = image_source
        self._playback_timer = QTimer()
        self._fps = 0
        self._last_update = None
        self._fps_update_counter = 0

        self._build_ui()

        self.roi_visualizer = ROIVisualizer(self._image_canvas, roi_manager)

        self._connect_signals()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self._image_canvas = ImageCanvas(self)
        self._image_canvas.clear()

        layout.addWidget(self._image_canvas)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        layout.addWidget(self.slider)

        button_row = QHBoxLayout()
        self.btn_first = QPushButton("||◀")
        self.btn_prev = QPushButton("|◀")
        self.btn_play = QPushButton("▶")
        self.btn_next = QPushButton("▶|")
        self.btn_last = QPushButton("▶||")

        for btn in (
            self.btn_first,
            self.btn_prev,
            self.btn_play,
            self.btn_next,
            self.btn_last,
        ):
            btn.setFixedHeight(28)
            # btn.setEnabled(False)
            button_row.addWidget(btn)

        button_row.addStretch()

        self.frame_label = QLabel("Frame: 0/0")
        button_row.addWidget(self.frame_label)

        button_row.addStretch()

        self.fps_label = QLabel("Target FPS:")

        self.fps_selection = QComboBox()
        self.fps_selection.addItems(["1", "5", "10", "15", "30", "60", "native"])
        self.fps_selection.setCurrentText("10")
        self.fps_selection.setFixedSize(70, 28)

        self.real_fps = QLabel("FPS: 0")

        button_row.addWidget(self.fps_label)
        button_row.addWidget(self.fps_selection)

        button_row.addStretch()

        button_row.addWidget(self.real_fps)


        button_row.addStretch()

        self.lock_rois_checkbox = QCheckBox("Lock ROIs")
        button_row.addWidget(self.lock_rois_checkbox)


        layout.addLayout(button_row)



    def _connect_signals(self) -> None:
        self.btn_play.clicked.connect(self._toggle_playback)
        self.btn_first.clicked.connect(lambda: self._request_frame(0))
        self.btn_last.clicked.connect(lambda: self._request_frame(-1))
        self.btn_prev.clicked.connect(
            lambda: self._request_frame(self._current_frame - 1)
        )
        self.btn_next.clicked.connect(
            lambda: self._request_frame(self._current_frame + 1)
        )
        self.slider.valueChanged.connect(self._on_slider_changed)
        self._playback_timer.timeout.connect(self._request_next_frame)
        self.fps_selection.currentTextChanged.connect(self._on_fps_changed)

        self._image_source.source_loaded.connect(self._update)

        self.lock_rois.connect(self.roi_visualizer.lock_rois)

        # self._image_canvas.left_mouse_pressed.connect(
        #     self.roi_visualizer.on_mouse_press
        # )
        # self._image_canvas.left_mouse_moved.connect(self.roi_visualizer.on_mouse_move)
        # self._image_canvas.left_mouse_released.connect(
        #     self.roi_visualizer.on_mouse_release
        # )

        self._image_source.new_frame.connect(self._display_frame)

        self.lock_rois_checkbox.clicked.connect(lambda x: self.lock_rois.emit(x))

    def _request_frame(self, index: int) -> None:
        self._image_source.read_frame(index)

    def _request_next_frame(self) -> None:
        self._image_source.read_frame(self._current_frame + 1)

    @Slot(object)
    def _display_frame(self, frame: Optional[Frame]):
        if frame is not None:
            self._update_index(frame.index)
            self._image_canvas.set_image(frame.frame)
            self.frame_label.setText(
                f"Frame: {self._current_frame}/{self._image_source.frame_count}"
            )

            self._fps_update_counter += 1

            if self._fps_update_counter >= 10:  # update every 10 frames
                current_time = perf_counter()

                if self._last_update is not None:
                    fps = round(
                        self._fps_update_counter / (current_time - self._last_update),
                        1,
                    )
                    self.real_fps.setText(f"FPS: {fps}")
                self._last_update = current_time
                self._fps_update_counter = 0

    def _update_index(self, new_index: int):
        self._current_frame = new_index
        self.slider.blockSignals(True)
        self.slider.setValue(self._current_frame)
        self.slider.blockSignals(False)

    def _toggle_playback(self) -> None:
        self._playing = not self._playing
        self.btn_play.setText("❚❚" if self._playing else "▶")
        if self._playing:
            self._playback_timer.setInterval(int(1000 / self._fps))
            self._playback_timer.start()
        else:
            self._playback_timer.stop()

    def _on_slider_changed(self, value: int):
        self._request_frame(value)

    def _on_fps_changed(self, value: str):
        if value.startswith("native"):
            fps = self._image_source.fps
        else:
            fps = int(value)

        self._fps = fps
        if self._playing:
            self._toggle_playback()
            self._toggle_playback()

    def _update(self, info: SourceInfo):
        if self._playing:
            self._toggle_playback()

        self._current_frame = 0
        self._request_frame(0)
        self.fps_selection.setItemText(6, f"native: {info.fps}")
        self.fps_selection.setCurrentIndex(6)
        self._image_canvas.reset_view()
        self.slider.setMinimum(0)
        self.slider.setMaximum(info.frame_count)
