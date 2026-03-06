"""
main window class loading ui and connect function with manager
"""
import logging
import sys
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot, QThread, Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QMainWindow,
    QPushButton,
    QMessageBox,
    QProgressBar,
    QLabel,
    QTableWidget, QFileDialog,
    QTextBrowser, QCheckBox,
)

from solid_automate.core.solidworks_service import SolidWorksService

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class MainWindow(QMainWindow):
    """Main window class"""
    request_connect = Signal()
    request_disconnect = Signal()
    request_start_job = Signal(Path, list)

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

        # vars
        self.selected_dir = ""

        # load other tools
        self.thread = QThread()
        self.worker = SolidWorker()
        self.worker.moveToThread(self.thread)
        self.worker.connected.connect(self.on_connected)
        self.worker.disconnected.connect(self.on_disconnected)
        self.request_connect.connect(self.worker.connect_solidworks)
        self.request_disconnect.connect(self.worker.disconnect_solidworks)
        self.request_start_job.connect(self.worker.start_job)
        self.worker.error_creating_dir.connect(self.on_error_creating_dir)
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
        self.lbl_actual_path = self.ui_main.findChild(QLabel, 'lb_actual_path')
        self.tb_main = self.ui_main.findChild(QTableWidget, 'tb_main')
        self.status_label = self.ui_main.findChild(QLabel, 'status_label')
        self.tb_console = self.ui_main.findChild(QTextBrowser, 'tb_console')
        self.console_manager = TextBrowserManager(self.tb_console)
        self.cb_dxf = self.ui_main.findChild(QCheckBox, 'check_box_dxf')
        self.cb_pdf = self.ui_main.findChild(QCheckBox, 'check_box_pdf')
        self.cb_step = self.ui_main.findChild(QCheckBox, 'check_box_step')

        try:
            self.init_button_functions()
        except RuntimeError:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Error!")
            msg.setText("Error while loading application. Some functionality may not work.")
            msg.exec()

    def on_connected(self):
        """Function called when connection is established"""
        self.status_label.setText("Connected")
        self.console_manager.insert_text("Connected successful.")

    def on_disconnected(self):
        """Function called when disconnected"""
        self.status_label.setText("Disconnected")
        self.console_manager.insert_text("Disconnected successful.")
        self.btn_connect_solidworks.setEnabled(True)

    def on_error(self, error_msg):
        """Function called when error_msg occurs"""
        self.status_label.setText("Fail. Try to reconnect.")
        self.console_manager.insert_text(f"Error occurred. {error_msg}")
        self.btn_connect_solidworks.setEnabled(True)

    def on_error_creating_dir(self, error_msg):
        """Function called when error_msg occurs"""
        self.console_manager.insert_text(f"Error occurred while creating dir's. {error_msg}")

    def get_files_to_produce(self) -> list:
        """Function called when get_files_to_produce is called. Return state of checkbox's"""
        return [self.cb_pdf.checkState(), self.cb_step.checkState(), self.cb_dxf.checkState()]

    def init_button_functions(self) -> None:
        """Functions connect a button object with functions"""
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
        self.btn_connect_solidworks.setEnabled(False)
        self.status_label.setText("Connecting...")
        self.request_connect.emit()

    def f_disconnect_solid(self) -> None:
        """Function to disconnect solidworks"""
        self.request_disconnect.emit()

    def f_settings(self) -> None:
        """Function open settings page"""
        raise NotImplementedError("Settings not implemented")

    def f_select_dir(self) -> None:
        """Function open select dir page to choose a directory"""
        self.console_manager.insert_text("Selecting directory...")
        self.selected_dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        if self.selected_dir != "":
            display_text = f"{"/".join(self.selected_dir.split("/")[:2])}/.../{"/".join(self.selected_dir.split("/")[-2:])}"
            self.lbl_actual_path.setText(display_text)
            self.console_manager.insert_text(f"True: Selected directory: {self.selected_dir}")

    def f_start_job(self) -> None:
        """Function start job: selected file will be generated"""
        self.request_start_job.emit(self.selected_dir, self.get_files_to_produce())

    def f_stop_job(self) -> None:
        """Function stop actual preparing docs job"""
        raise NotImplementedError("Stopping job not implemented")

    def f_set_label_actual_path(self, actual_path) -> None:
        """Function set label actual path"""
        raise NotImplementedError("Setting label not implemented")


class SolidWorker(QObject):
    connected = Signal()
    disconnected = Signal()
    saved = Signal()
    settings = Signal()
    select_dir = Signal(str)
    error = Signal(str)
    error_creating_dir = Signal(str)
    message = Signal()
    job_progress = Signal(int, int)
    job_done = Signal(int)
    job_error = Signal(str)

    def __init__(self):
        super().__init__()
        self.sw = SolidWorksService()
        self.proj_path = None

    @Slot()
    def connect_solidworks(self):
        """Function connects solidworks"""
        try:
            self.sw.connect()
            self.connected.emit()
        except Exception as e:
            self.error.emit(e)

    @Slot()
    def disconnect_solidworks(self):
        """Function disconnects solidworks"""
        self.sw.shutdown()
        self.disconnected.emit()

    @staticmethod
    def check_doc_dir_exist(path) -> bool:
        """Function check if doc dir exist"""
        ddir = ["DXF", "PDF", "STEP"]
        doc_pth = Path(path) / "Dokumentacja"
        Path(doc_pth).mkdir(parents=True, exist_ok=True)
        for d in ddir:
            sub_dir = doc_pth / d
            Path(sub_dir).mkdir(parents=True, exist_ok=True)
        if not doc_pth.exists():
            return False
        return True

    def open_part(self, path):
        try:
            result = self.sw.open_part(path)
            self.message.emit(result)
        except Exception as e:
            self.error.emit(e)

    @Slot()
    def start_job(self, path: Path, types_to_produce: list):
        """Function start job: selected file type will be generated"""
        if not self.check_doc_dir_exist(path):
            self.error.emit(f"Document dir not created: {path}")
            return
        _pdf, _step, _dxf = types_to_produce
        if _pdf == Qt.CheckState.Checked:
            print("make PDF")
        if _step == Qt.CheckState.Checked:
            print("make Step")
        if _dxf == Qt.CheckState.Checked:
            print("make DXF")


class TextBrowserManager:
    """Console browser class"""

    def __init__(self, browser: QTextBrowser):
        self.browser = browser

    def clear(self):
        """Function clear text in text browser"""
        self.browser.clear()

    def insert_text(self, text):
        """Function insert text in text browser"""
        cursor = self.browser.textCursor()
        cursor.movePosition(QTextCursor.Start)
        cursor.insertText(text + "\n")

        # set cursor on beginning and scroll max up
        self.browser.setTextCursor(cursor)
        self.browser.verticalScrollBar().setValue(0)
