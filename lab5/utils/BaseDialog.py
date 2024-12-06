from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

class BaseDialog(QDialog):
    def __init__(self, width, height, title, parent=None, modal=False, controls=True):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(width, height)
        self.setModal(modal)
        if controls:
            self.setWindowFlags(
                Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint
            )
        else:
            self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint)