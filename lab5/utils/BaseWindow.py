from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt

class BaseWindow(QMainWindow):
    def __init__(self, width, height, title, is_main=True, controls=True):
        super().__init__()

        self.setWindowTitle(title)
        self.resize(width, height)

        if controls:
            self.setWindowFlags(
                Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint
            )
        else:
            self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)

        if not is_main:
            self.setWindowModality(Qt.ApplicationModal)