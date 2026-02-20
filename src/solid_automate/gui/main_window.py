import sys
from pathlib import Path

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    """Main window class"""

    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        if getattr(sys, 'frozen', False):
            raise Exception("Setup path if app is packed")
        else:
            ui_main_file = Path(__file__).resolve().parent / "ui" / "solid_automate.ui"

        self.ui_main = loader.load(ui_main_file)
        self.setCentralWidget(self.ui_main)
