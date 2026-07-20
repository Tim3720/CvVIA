from ntpath import isfile
import os
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

import cv2
import numpy as np
import pydicom as dicom
from PySide6.QtCore import QObject, Signal


class SourceType(Enum):
    VIDEO = auto()
    IMAGES = auto()
    DCOM = auto()
    NPY = auto()


@dataclass
class Frame:
    frame: np.ndarray
    index: int


IMAGE_EXTENSIONS = (
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tiff",
    ".tif",
    ".webp",
)


@dataclass
class SourceInfo:
    """Metadata about the loaded source — read-only snapshot."""

    source_type: SourceType
    path: str
    frame_count: int
    fps: float
    width: int
    height: int

    @property
    def duration_seconds(self) -> float:
        return self.frame_count / self.fps if self.fps > 0 else 0.0


class ImageSource(QObject):
    source_loaded = Signal(object)
    new_frame = Signal(object)

    def __init__(self):
        super().__init__()
        self._cap: Optional[cv2.VideoCapture] = None
        self._image_paths: list[str] = []
        self._info: Optional[SourceInfo] = None
        self._images: Optional[np.ndarray] = None

        self._current_frame: Optional[Frame] = None


    def load_source(self, path: str):
        # first try to get the type of source:
        if os.path.isfile(path):    # either video or .npy file
            if path.endswith((".npy", ".npz")):
                return self.load_npy(path, 30)
            else:
                return self.load_video(path)
        elif os.path.isdir(path):
            files = os.listdir(path)
            for file in files:
                if file.endswith(IMAGE_EXTENSIONS):
                    return self.load_folder(path, 30)
                elif file.lower().endswith(".dcm"):
                    return self.load_dicom(path, 30)

    def load_video(self, path: str) -> SourceInfo:
        self.release()
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {path}")

        info = SourceInfo(
            source_type=SourceType.VIDEO,
            path=path,
            frame_count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            fps=cap.get(cv2.CAP_PROP_FPS) or 10.0,
            width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )

        self._cap = cap
        self._info = info

        self.source_loaded.emit(info)
        return info

    def load_folder(self, path: str, fps: int = 10) -> SourceInfo:
        self.release()
        if not os.path.isdir(path):
            raise ValueError(f"Directory {path} does not exist")

        files = [
            os.path.join(path, f)
            for f in os.listdir(path)
            if f.lower().endswith(IMAGE_EXTENSIONS)
        ]

        if not files:
            raise ValueError(f"No image files found in {path}")

        files.sort()

        self._image_paths = files

        first_frame = cv2.imread(files[0])

        info = SourceInfo(
            source_type=SourceType.IMAGES,
            path=path,
            frame_count=len(files),
            fps=fps,
            width=first_frame.shape[1],
            height=first_frame.shape[0],
        )

        self._info = info
        self.source_loaded.emit(info)
        return info

    def load_dicom(self, path: str, fps: int = 10) -> SourceInfo:
        self.release()
        if not os.path.isdir(path):
            raise ValueError(f"Directory {path} does not exist")

        files = [
            os.path.join(path, f)
            for f in os.listdir(path)
            if f.lower().endswith(".dcm")
        ]

        if not files:
            raise ValueError(f"No DCOM files found in {path}")

        files.sort()

        self._image_paths = files

        first_frame = dicom.dcmread(files[0]).pixel_array

        info = SourceInfo(
            source_type=SourceType.DCOM,
            path=path,
            frame_count=len(files),
            fps=fps,
            width=first_frame.shape[1],
            height=first_frame.shape[0],
        )

        self._info = info
        self.source_loaded.emit(info)
        return info


    def load_npy(self, path: str, fps: int = 10) -> SourceInfo:
        data = np.load(path)
        print(data.shape)

        self._images = data

        info = SourceInfo(
            source_type=SourceType.NPY,
            path=path,
            frame_count=data.shape[0],
            fps=fps,
            width=data.shape[2],
            height=data.shape[1],
        )

        self._info = info
        self.source_loaded.emit(info)
        return info


    def read_frame(self, index: int):
        if self._info is None:
            return

        # index = (index + self._info.frame_count) % self._info.frame_count

        if (index < 0):
            index = self._info.frame_count + index

        if (index >= self._info.frame_count):
            index = self._info.frame_count
            return

        if self._info.source_type == SourceType.VIDEO:
            frame = self._read_video_frame(index)
        elif self._info.source_type == SourceType.DCOM:
            frame = self._read_dicom_frame(index)
        elif self._info.source_type == SourceType.NPY:
            frame = self._read_npy_frame(index)
        else:
            frame = self._read_folder_frame(index)

        self._current_frame = frame
        self.new_frame.emit(frame)

    def reload_frame(self):
        self.new_frame.emit(self._current_frame)

    def _read_video_frame(self, index: int) -> Optional[Frame]:
        if self._cap is None:
            return None

        self._cap.set(cv2.CAP_PROP_POS_FRAMES, index)
        ok, frame = self._cap.read()

        if ok:
            _frame = Frame(frame, index)
            return _frame
        else:
            return None

    def _read_folder_frame(self, index: int) -> Optional[Frame]:
        if not self._image_paths:
            return None

        frame = cv2.imread(self._image_paths[index])
        return Frame(frame, index)

    def _read_dicom_frame(self, index: int) -> Optional[Frame]:
        if not self._image_paths:
            return None

        path = self._image_paths[index]
        ds = dicom.dcmread(path)
        ds_array = ds.pixel_array

        frame = cv2.normalize(ds_array, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        return Frame(frame, index)

    def _read_npy_frame(self, index: int) -> Optional[Frame]:
        if self._images is None:
            return None

        frame = self._images[index]
        return Frame(frame, index)


    @property
    def info(self) -> Optional[SourceInfo]:
        return self._info

    @property
    def is_loaded(self) -> bool:
        return self._info is not None

    @property
    def frame_count(self) -> int:
        return self._info.frame_count if self._info else 0

    @property
    def fps(self) -> float:
        return self._info.fps if self._info else 10.0

    def release(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        self._image_paths = []
        self._info = None

    def __del__(self) -> None:
        self.release()
