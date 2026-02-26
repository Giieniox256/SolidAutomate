"""
main window class loading ui and connect function with manager
"""
import logging
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QMessageBox,
    QProgressBar,
    QLabel,
    QTableWidget,
)

from solid_automate.core.solidworks_service import SolidWorksService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class MainWindow(QMainWindow):
    """Main window class"""
    request_connect = Signal()
    request_disconnect = Signal()

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

        # load other tools
        self.thread = QThread()
        self.worker = SolidWorker()
        self.worker.moveToThread(self.thread)
        self.request_connect.connect(self.worker.connect_solidworks)

        self.thread.start()

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
        self.status_label = self.ui_main.findChild(QLabel, 'status_label')

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
        Functions connect a button object with functions
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

    def f_connect_solid(self) -> None:
        """Function to connect with solidworks"""
        self.status_label.setText("Connecting...")
        self.request_connect.emit()
        self.status_label.setText("Connected")

    def f_disconnect_solid(self) -> None:
        """Function to disconnect solidworks"""
        self.request_disconnect.emit()
        self.status_label.setText("Disconnected...")

    def f_settings(self) -> None:
        """Function open settings page"""
        raise NotImplementedError("Settings not implemented")

    def f_select_dir(self) -> None:
        """Function open select dir page to choose a directory"""
        raise NotImplementedError("Selection of Dir not implemented")

    def f_start_job(self) -> None:
        """Function start job: selected file will be generated"""
        raise NotImplementedError("Starting job not implemented")

    def f_stop_job(self) -> None:
        """Function stop actual preparing docs job"""
        raise NotImplementedError("Stopping job not implemented")

    def f_set_label_actual_path(self, actual_path) -> None:
        """Function set label actual path"""
        raise NotImplementedError("Setting label not implemented")


class SolidWorker(QObject):
    connected = Signal()
    saved = Signal()
    settings = Signal()
    select_dir = Signal()
    error = Signal()
    message = Signal()

    def __init__(self):
        super().__init__()
        self.sw = SolidWorksService()

    @Slot()
    def connect_solidworks(self):
        """Function connects solidworks"""
        try:
            self.sw.connect()
        except Exception as e:
            self.error.emit(e)

    @Slot()
    def open_part(self, path):
        try:
            result = self.sw.open_part(path)
            self.message.emit(result)
        except Exception as e:
            self.error.emit(e)

    @Slot()
    def disconnect_solidworks(self):
        """Function disconnects solidworks"""
        self.sw.shutdown()

