import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget

plt.style.use("dark_background")


class FigureOutput(QWidget):
    def __init__(self):
        super().__init__()

        self.figure = Figure()
        plt.ion()

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.canvas = FigureCanvas(self.figure)

        layout.addWidget(self.canvas)

    def redraw(self):
        self.canvas.draw()

    def clear(self):
        for ax in self.figure.axes:
            ax.clear()
        self.figure.clear()
