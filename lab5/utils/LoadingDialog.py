import os

import stanza
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QProgressBar

import spacy
from lab5.utils.BaseDialog import BaseDialog

def is_model_downloaded(lang):
    model_dir = os.path.join(stanza.resources.common.DEFAULT_MODEL_DIR, lang)
    return os.path.exists(model_dir)

class LoadingDialog(BaseDialog):
    def __init__(self, parent=None, message="Завантаження моделі, будь ласка, зачекайте..."):
        super().__init__(300, 100, "Завантаження моделі", parent)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel(message)
        layout.addWidget(label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        layout.addWidget(self.progress_bar)

class DownloadModelThread(QThread):
    finished = pyqtSignal()

    def __init__(self, lang):
        super().__init__()
        self.lang = lang

    def run(self):
        stanza.download(self.lang, verbose=False)
        self.finished.emit()


class DownloadSpacyModelThread(QThread):
    finished = pyqtSignal()

    def __init__(self, model_name):
        super().__init__()
        self.model_name = model_name

    def run(self):
        spacy.cli.download(self.model_name)
        self.finished.emit()