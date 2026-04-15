from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.widgets.figure_output import FigureOutput

from .models.image_source import ImageSource
from .models.roi import ROIManager
from .services.script_runner import ScriptRunner
from .widgets.frame_output import FrameOutput
from .widgets.roi_output import ROIOutput
from .widgets.script_output_view import ScriptOutputView
from .widgets.source_view import SourceView


class MainWindow(QMainWindow):
    def __init__(self, source_path: str = "", script_path: str = "") -> None:
        super().__init__()
        self.setWindowTitle("CvVIA")
        self.resize(1600, 900)

        self.image_source = ImageSource()
        self.roi_manager = ROIManager()

        self._build_menu()
        self._build_ui()

        self.script_runner = ScriptRunner(
            self.image_source,
            self.roi_manager,
            self.frame_output,
            self.roi_output,
            self.fig_output,
            self,
        )

        self._connect_signals()

        if source_path:
            self.image_source.load_source(source_path)

        if script_path:
            self.script_runner.load(script_path)

    def _build_ui(self):
        central_widget = QWidget()
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(0, 0, 0, 0)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        self.source_view = SourceView(self.image_source, self.roi_manager, self)
        self.main_splitter.addWidget(self.source_view)

        self.tabs = QTabWidget()
        self.frame_output = FrameOutput()
        self.roi_output = ROIOutput()
        self.fig_output = FigureOutput()
        self.tabs.addTab(self.frame_output, "Frame Output")
        self.tabs.addTab(self.roi_output, "ROIs")
        self.tabs.addTab(self.fig_output, "Plots")

        self.main_splitter.addWidget(self.tabs)

        self.script_output = ScriptOutputView()

        central_layout.addWidget(self.main_splitter, 1)
        # central_layout.addStretch()
        central_layout.addWidget(self.script_output)

        self.setCentralWidget(central_widget)

    def _build_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("&File")

        self.act_open_video = QAction("Open &Video…", self)
        self.act_open_video.setShortcut(QKeySequence("Ctrl+O"))
        file_menu.addAction(self.act_open_video)

        self.act_open_folder = QAction("Open &Folder…", self)
        self.act_open_folder.setShortcut(QKeySequence("Ctrl+Shift+O"))
        file_menu.addAction(self.act_open_folder)

        self.act_open_dicom = QAction("Open DICOM…", self)
        file_menu.addAction(self.act_open_dicom)

        self.act_open_npy = QAction("Open .npy…", self)
        file_menu.addAction(self.act_open_npy)

        file_menu.addSeparator()

        view_menu = menubar.addMenu("&View")

        roi_menu = menubar.addMenu("ROI")
        self.act_delete_all_rois = QAction("Delete all ROIs")
        roi_menu.addAction(self.act_delete_all_rois)

        script_menu = menubar.addMenu("&Script")

        self.act_create_new_script = QAction("Create New &Script")
        self.act_create_new_script.setShortcut(QKeySequence("Ctrl+N"))
        script_menu.addAction(self.act_create_new_script)

        self.act_load_script = QAction("&Load Script")
        script_menu.addAction(self.act_load_script)

        self.act_reload_script = QAction("Reload Script")
        self.act_reload_script.setShortcut(QKeySequence("Ctrl+R"))
        script_menu.addAction(self.act_reload_script)

        self.act_save_data = QAction("Save data")
        script_menu.addAction(self.act_save_data)

        bulk_menu = menubar.addMenu("&Bulk")

    def _connect_signals(self):
        self.act_open_video.triggered.connect(self._open_video)
        self.act_open_folder.triggered.connect(self._open_folder)
        self.act_open_dicom.triggered.connect(self._open_dicom)
        self.act_open_npy.triggered.connect(self._open_npy)

        self.act_load_script.triggered.connect(self._load_script)
        self.act_reload_script.triggered.connect(self.script_runner.on_reload)
        self.act_save_data.triggered.connect(self.script_runner.save_data)

        self.act_delete_all_rois.triggered.connect(
            self.source_view.roi_visualizer.delete_all_rois
        )

        # self.source_view.lock_rois.connect(self.roi_manager.lock_rois)


    def ask_save_path(self):
        return QFileDialog.getExistingDirectory(self, "Save to:")

    def _open_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Video",
            filter="Video files (*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm);;All files (*)",
        )
        if not path:
            return

        self.image_source.load_video(path)

    def _open_folder(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "Open Image Folder",
        )
        if not path:
            return

        # get fps:
        fps, ok = QInputDialog.getInt(
            None,  # parent
            "FPS",  # window title
            "FPS:",  # label text
            10,  # default value
            1,  # min
            1000,  # max
            1,  # step
        )

        if not ok:
            fps = 10

        self.image_source.load_folder(path, fps)

    def _open_dicom(self):
        path = QFileDialog.getExistingDirectory(self, "Open DICOM Folder")
        if not path:
            return

        # get fps:
        fps, ok = QInputDialog.getInt(
            None,  # parent
            "FPS",  # window title
            "FPS:",  # label text
            10,  # default value
            1,  # min
            1000,  # max
            1,  # step
        )

        if not ok:
            fps = 10

        self.image_source.load_dicom(path, fps)


    def _open_npy(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open .npy file")
        print(path)
        if not path:
            return

        # get fps:
        fps, ok = QInputDialog.getInt(
            None,  # parent
            "FPS",  # window title
            "FPS:",  # label text
            10,  # default value
            1,  # min
            1000,  # max
            1,  # step
        )

        if not ok:
            fps = 10

        self.image_source.load_npy(path, fps)



    def _load_script(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Script",
            "./",
        )
        if not path:
            return

        self.script_runner.load(path)
