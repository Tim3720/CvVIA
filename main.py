import sys
import argparse
import traceback
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow


def handle_exception(exc_type, exc_value, exc_traceback):
    traceback.print_exception(exc_type, exc_value, exc_traceback)


sys.excepthook = handle_exception




parser = argparse.ArgumentParser()
parser.add_argument("--input", default="", nargs="?")
parser.add_argument("--script", default="", nargs="?")

args = parser.parse_args()
input = args.input
script = args.script


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CvVIA")
    app.setOrganizationName("Geomar")

    # Load stylesheet
    app.setStyle("Fusion")
    qss_path = Path(__file__).parent / "app" / "style.qss"
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))

    window = MainWindow(input, script)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
