import pythoncom
import win32com.client
from PySide6.QtCore import QObject, Signal


class SolidWorksService(QObject):
    connected = Signal()
    disconnected = Signal()
    error = Signal()

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

        if hasattr(self, "initialized"):
            return

        self.initialized = True
        self.sw = None

    def connect(self):
        if self.sw:
            self.connected.emit()
            return
        try:
            pythoncom.CoInitialize()

            try:
                self.sw = win32com.client.GetActiveObject("SldWorks.Application")
            except:
                self.sw = win32com.client.Dispatch("SldWorks.Application")

            self.sw.Visible = True
            self.connected.emit()
        except Exception as e:
            self.error.emit(str(e))

    def disconnect(self):
        self.sw = None
        pythoncom.CoUninitialize()
        self.disconnected.emit()
