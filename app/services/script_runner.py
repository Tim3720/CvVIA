import importlib.util
import os
import sys
from typing import Optional

import numpy as np
from PySide6.QtCore import QFileSystemWatcher, QObject, QRectF, QTimer, Signal, Slot

from app.models.image_source import Frame, ImageSource
from app.models.roi import ROIManager
from app.widgets.figure_output import FigureOutput
from app.widgets.frame_output import FrameOutput
from app.widgets.roi_output import ROIOutput


class ScriptLoader(QObject):
    script_reloaded = Signal()

    def __init__(self, script_path):
        super().__init__()
        self.script_path = os.path.abspath(script_path)
        self.module_name = os.path.basename(script_path).split(".")[0]
        self.module = None

        # Setup the file watcher
        self.watcher = QFileSystemWatcher([self.script_path])
        self.watcher.fileChanged.connect(self._on_file_changed)

    def _on_file_changed(self, path):
        """Internal slot triggered by the QFileSystemWatcher."""
        # 1. Re-add the path to the watcher (Crucial for Atomic Saves)
        # We use a tiny delay because some editors delete/recreate the file
        # very quickly, and the file might not be "there" yet.
        QTimer.singleShot(100, lambda: self._handle_reload(path))

    def _handle_reload(self, path):
        # Ensure the file is back in the watcher's list
        if path not in self.watcher.files():
            self.watcher.addPath(path)

        print(f"Change detected in {path}. Reloading...")
        if self.load_script():
            self.script_reloaded.emit()

    def load_script(self):
        try:
            # Re-create the spec to ensure we get the fresh content from disk
            spec = importlib.util.spec_from_file_location(
                self.module_name, self.script_path
            )

            if spec is None or spec.loader is None:
                print("Failed to load script spec.")
                return False

            # Create module and update sys.modules
            self.module = importlib.util.module_from_spec(spec)
            sys.modules[self.module_name] = self.module

            # Execute the module to populate functions
            spec.loader.exec_module(self.module)
            return True
        except Exception as e:
            print(f"Failed to load script: {e}")
            return False

    def call_function(self, func_name, *args, **kwargs):
        """Safely calls a function if it exists in the loaded script."""
        if self.module and hasattr(self.module, func_name):
            func = getattr(self.module, func_name)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                import traceback
                traceback.print_exc()
                return None
        else:
            print(f"Function '{func_name}' not found in {self.module_name}")
            return None


class ScriptRunner:
    def __init__(
        self,
        image_source: ImageSource,
        roi_manager: ROIManager,
        frame_output: FrameOutput,
        roi_output: ROIOutput,
        fig_output: FigureOutput,
        parent,
    ) -> None:
        self.script_loader: Optional[ScriptLoader] = None
        self._script_path: Optional[str] = None

        self.parent = parent
        self._image_source = image_source
        self._roi_manager = roi_manager
        self._frame_output = frame_output
        self._roi_output = roi_output
        self._fig_output = fig_output
        self._lock_roi = False

        self._connect_signals()

    def _connect_signals(self):
        self._image_source.new_frame.connect(self.on_new_frame)
        self._roi_manager.rect_moved.connect(self.on_roi_change)

    def load(self, path: str):
        self.script_loader = ScriptLoader(path)
        self.script_loader.load_script()
        self._script_path = path
        self.script_loader.script_reloaded.connect(self.on_reload)

        self._setup()
        self._image_source.reload_frame()

    def _setup(self):
        if self.script_loader is None:
            return
        self.script_loader.call_function("setup", self._fig_output.figure)

    def on_reload(self):
        self._fig_output.clear()
        self._setup()
        self._image_source.reload_frame()

    def on_roi_change(self):
        # just trigger frame reload, as this will trigger recomputing of the rois
        self._image_source.reload_frame()

    @Slot(np.ndarray)
    def on_new_frame(self, _frame: Optional[Frame]):
        if self.script_loader is None or _frame is None:
            return

        frame_org = Frame(_frame.frame.copy(), _frame.index)
        frame_processed = Frame(_frame.frame.copy(), _frame.index)

        self.process_frame(frame_processed)

        self.process_roi(frame_org, frame_processed)

        self._fig_output.redraw()

    def process_frame(self, frame: Frame):
        if self.script_loader is None:
            return

        res = self.script_loader.call_function(
            "process_frame", frame.frame, frame.index, self._fig_output.figure
        )

        if res is not None:
            frame.frame = res

        self._frame_output.show_output(frame)

    def process_roi(self, frame_org: Frame, frame_processed: Frame):
        if self.script_loader is None:
            return

        rois = []
        for idx, roi in self._roi_manager.rois.items():
            rect = roi.rect.toAlignedRect()
            x = rect.x()
            y = rect.y()
            w = rect.width()
            h = rect.height()

            roi_org = frame_org.frame[y : y + h, x : x + w].copy()
            roi_processed = frame_processed.frame[y : y + h, x : x + w].copy()
            roi_rect = np.array([x, y, w, h])

            res = self.script_loader.call_function(
                "process_roi",
                roi_rect,
                roi_org,
                roi_processed,
                idx,
                frame_org.index,
                len(self._roi_manager.rois),
                self._fig_output.figure,
            )
            rois.append((res, idx))

            new_rect = QRectF(*roi_rect)
            roi.change_rect(new_rect)
            # self._roi_manager.move_roi_no_signal(new_rect, idx)

            # new_rect = QRectF(*roi_rect)
            # self._roi_manager.move_roi(new_rect, idx, True)


        rois.sort(key=lambda x: x[1])
        self._roi_output.update_rois(rois)

    def save_data(self):
        if self.script_loader is None:
            return

        file_path = self.parent.ask_save_path()
        self.script_loader.call_function("save_data", self._fig_output.figure, file_path)
