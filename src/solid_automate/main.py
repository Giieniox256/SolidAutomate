"""Main file to run application"""
import sys

from PySide6 import QtWidgets

from solid_automate.gui import main_window

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = main_window.MainWindow()
    window.show()
    sys.exit(app.exec_())
