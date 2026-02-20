"""
main window class loading ui and connect function with manager
"""
import sys
from pathlib import Path

from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QMessageBox,
    QProgressBar,
    QLabel,
    QTableWidget,
)


class MainWindow(QMainWindow):
    """Main window class"""

    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        if getattr(sys, 'frozen', False):
            raise Exception("Setup path if app is packed")
        else:
            ui_main_file = Path(__file__).resolve().parent / "ui" / "solid_automate.ui"

        # load ui from .ui
        self.ui_main = loader.load(ui_main_file)
        self.setCentralWidget(self.ui_main)

        # setup tile
        self.setWindowTitle("SolidAutomate")

        # assign widget objects with variables
        self.btn_connect_solidworks = self.ui_main.findChild(QPushButton, 'btn_connect_solid')
        self.btn_disconnect_solidworks = self.ui_main.findChild(QPushButton, 'btn_disconnect_solid')
        self.btn_settings = self.ui_main.findChild(QPushButton, 'btn_settings')
        self.btn_select_dir = self.ui_main.findChild(QPushButton, 'btn_select_dir')
        self.btn_start_job = self.ui_main.findChild(QPushButton, 'btn_start_job')
        self.btn_stop_job = self.ui_main.findChild(QPushButton, 'btn_stop_job')
        self.progress_bar = self.ui_main.findChild(QProgressBar, 'progress_bar')
        self.lbl_actual_path = self.ui_main.findChild(QLabel, 'lbl_actual_path')
        self.tb_main = self.ui_main.findChild(QTableWidget, 'tb_main')

        try:
            self.init_button_functions()
        except RuntimeError:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error!")
            msg.setText("Error while loading application. Some functionality may not work.")
            msg.exec()

    def init_button_functions(self) -> None:
        """
        Functions connect button object with functions
        """
        # connect widgets with function
        if self.btn_connect_solidworks is not None:
            self.btn_connect_solidworks.clicked.connect(self.f_connect_solid)
        if self.btn_disconnect_solidworks is not None:
            self.btn_disconnect_solidworks.clicked.connect(self.f_disconnect_solid)
        if self.btn_settings is not None:
            self.btn_settings.clicked.connect(self.f_settings)
        if self.btn_select_dir is not None:
            self.btn_select_dir.clicked.connect(self.f_select_dir)
        if self.btn_start_job is not None:
            self.btn_start_job.clicked.connect(self.f_start_job)
        if self.btn_stop_job is not None:
            self.btn_stop_job.clicked.connect(self.f_stop_job)
        if self.progress_bar is not None:
            self.progress_bar.setValue(0)

    def f_connect_solid(self):
        """Function to connect with solidworks"""
        raise NotImplementedError("Connection not implemented")

    def f_disconnect_solid(self):
        """Function to disconnect solidworks"""
        raise NotImplementedError("Disconnection not implemented")

    def f_settings(self):
        """Function open settings page"""
        raise NotImplementedError("Settings not implemented")

    def f_select_dir(self):
        """Function open select dir page to choose a directory"""
        raise NotImplementedError("Selection of Dir not implemented")

    def f_start_job(self):
        """Function start job: selected file will be generated"""
        raise NotImplementedError("Starting job not implemented")

    def f_stop_job(self):
        """Function stop actual preparing docs job"""
        raise NotImplementedError("Stopping job not implemented")

    def f_set_label_actual_path(self, actual_path):
        """Function set label actual path"""
        raise NotImplementedError("Setting label not implemented")
