import sys
from datetime import datetime

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget

from app.services.global_stream import GlobalStream


class ScriptOutputView(QWidget):
    MAX_LINES = 1000

    def __init__(self):
        super().__init__()
        self._build_ui()
        self.setup_global_logging()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("background-color: #14161a")

        layout.addWidget(self.output)

    def _append(self, text: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.output.appendPlainText(f"[{timestamp}] {text}")

        # auto-scroll
        self.output.moveCursor(QTextCursor.MoveOperation.End)

        self._trim_output()

    def info(self, text: str):
        self._append(f"[INFO] {text}")

    def error(self, text: str):
        self._append(f"[ERROR] {text}")

    def debug(self, text: str):
        self._append(f"[DEBUG] {text}")

    def setup_global_logging(self):
        self.stdout_stream = GlobalStream()
        self.stderr_stream = GlobalStream()

        self.stdout_stream.text_written.connect(self.info)
        self.stderr_stream.text_written.connect(self.error)

        sys.stdout = self.stdout_stream
        sys.stderr = self.stderr_stream

    def _trim_output(self):
        doc = self.output.document()

        if doc.blockCount() > self.MAX_LINES:
            cursor = QTextCursor(doc)

            # Move to first line
            cursor.movePosition(QTextCursor.MoveOperation.Start)

            # Select excess lines
            excess = doc.blockCount() - self.MAX_LINES

            for _ in range(excess):
                cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.KeepAnchor)

            cursor.removeSelectedText()
            cursor.deleteChar()
