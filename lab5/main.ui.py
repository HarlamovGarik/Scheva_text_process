import re
import sys
import os
from collections import Counter

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QSizePolicy,
    QButtonGroup, QRadioButton, QGroupBox, QMessageBox, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtGui import QPainter
import stanza
from lab5.parser import ScenarioParser, NewsParser, ArticleParser

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

nltk.download('punkt_tab')
nltk.download('stopwords')


def is_model_downloaded(lang):
    model_dir = os.path.join(stanza.resources.common.DEFAULT_MODEL_DIR, lang)
    return os.path.exists(model_dir)


class DownloadModelThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, lang):
        super().__init__()
        self.lang = lang

    def run(self):
        stanza.download(self.lang, verbose=False)
        self.finished.emit()


class NERApp(QWidget):
    def __init__(self):
        super().__init__()
        self.chart = None
        self.series = None
        self.left_layout = None

        self.language = 'uk'
        self.nlp = None
        self.parser = None
        self.nlp_models = {}
        self.init_ui()

        self.setup_nlp()

    def update_pie_chart(self, entity_counts):
        if hasattr(self, 'chart_view'):
            self.left_layout.removeWidget(self.chart_view)
            self.chart_view.deleteLater()
            self.chart_view = None

        self.series = QPieSeries()
        for entity_type, count in entity_counts.items():
            self.series.append(entity_type, count)

        self.chart = QChart()
        self.chart.addSeries(self.series)

        self.chart.setTitle("Розподіл іменованих сутностей")
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignBottom)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.chart_view.setFixedHeight(300)  # Встановлюємо розміри

        self.left_layout.addWidget(self.chart_view)

    def init_ui(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        left_widget = QWidget()
        self.left_layout = QVBoxLayout()
        left_widget.setLayout(self.left_layout)

        model_groupbox = QGroupBox("Вибір моделі")
        model_layout = QVBoxLayout()
        model_groupbox.setLayout(model_layout)

        self.language_group = QButtonGroup(self)
        self.ukrainian_button = QRadioButton("Українська")
        self.english_button = QRadioButton("Англійська")

        self.language_group.addButton(self.ukrainian_button)
        self.language_group.addButton(self.english_button)

        # Встановлюємо українську мову за замовчуванням
        self.ukrainian_button.setChecked(True)
        self.language = 'uk'  # Мова за замовчуванням

        # Підключаємо сигнал зміни вибраної мови
        self.language_group.buttonClicked.connect(self.change_language)

        # Додаємо кнопки вибору мови до layout моделі
        model_layout.addWidget(self.ukrainian_button)
        model_layout.addWidget(self.english_button)

        # Друга група: Вибір сайту
        site_groupbox = QGroupBox("Вибір сайту")
        site_layout = QVBoxLayout()
        site_groupbox.setLayout(site_layout)

        # Група кнопок для вибору типу парсера
        self.parser_group = QButtonGroup(self)

        self.scenario_button = QRadioButton("Сценарії")
        self.news_button = QRadioButton("Новини")
        self.article_button = QRadioButton("Наукова стаття")

        self.parser_group.addButton(self.scenario_button)
        self.parser_group.addButton(self.news_button)
        self.parser_group.addButton(self.article_button)

        # Встановлюємо кнопку "Новини" як вибрану за замовчуванням
        self.news_button.setChecked(True)
        self.parser = NewsParser()

        # Підключаємо сигнал зміни вибраної кнопки
        self.parser_group.buttonClicked.connect(self.change_parser)

        # Додаємо кнопки вибору парсера до layout сайту
        site_layout.addWidget(self.scenario_button)
        site_layout.addWidget(self.news_button)
        site_layout.addWidget(self.article_button)

        # Третя група: Ввід URL
        url_groupbox = QGroupBox("Ввід URL")
        url_layout = QVBoxLayout()
        url_groupbox.setLayout(url_layout)

        # Поле вводу URL та кнопка
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Введіть URL")
        self.process_button = QPushButton("Обробити")
        self.process_button.clicked.connect(self.process_text)

        # Додаємо поле вводу URL та кнопку до layout URL
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.process_button)

        # Додаємо групи до лівого лейауту
        self.left_layout.addWidget(model_groupbox)
        self.left_layout.addWidget(site_groupbox)
        self.left_layout.addWidget(url_groupbox)
        self.left_layout.addStretch()

        # Права частина (60%)
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        # Поле виводу тексту
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)

        # Поле виводу іменованих сутностей
        self.entities_output = QTextEdit()
        self.entities_output.setReadOnly(True)

        right_layout.addWidget(QLabel("Вилучений текст:"))
        right_layout.addWidget(self.text_output)
        right_layout.addWidget(QLabel("Знайдені іменовані сутності:"))
        right_layout.addWidget(self.entities_output)

        # Додавання віджетів до головного лейауту
        main_layout.addWidget(left_widget)
        main_layout.addWidget(right_widget)

        # Налаштування вікна
        self.setWindowTitle("NER Вилучення іменованих сутностей")
        self.resize(800, 600)
        self.show()

    def setup_nlp(self):
        if self.language in self.nlp_models:
            self.nlp = self.nlp_models[self.language]
        else:
            # Перевіряємо, чи модель вже завантажена
            if not is_model_downloaded(self.language):
                # Показуємо повідомлення про завантаження моделі
                loading_msg = QMessageBox(self)
                loading_msg.setWindowTitle("Завантаження моделі")
                loading_msg.setText(f"Завантаження моделі для мови '{self.language}', будь ласка, зачекайте...")
                loading_msg.setStandardButtons(QMessageBox.NoButton)
                loading_msg.setModal(True)
                loading_msg.show()
                QApplication.processEvents()

                # Завантаження моделі в окремому потоці
                self.download_thread = DownloadModelThread(self.language)
                self.download_thread.finished.connect(loading_msg.close)
                self.download_thread.start()
                self.download_thread.wait()  # Чекаємо завершення завантаження

            self.nlp = stanza.Pipeline(self.language, processors='tokenize,ner', verbose=False)
            self.nlp_models[self.language] = self.nlp

    def change_language(self, button):
        if button == self.ukrainian_button:
            self.language = 'uk'
        elif button == self.english_button:
            self.language = 'en'
        self.nlp = None  # Скидаємо модель, щоб вона перезавантажилася з новою мовою

    def change_parser(self, button):
        if button == self.scenario_button:
            self.parser = ScenarioParser()
        elif button == self.news_button:
            self.parser = NewsParser()
        elif button == self.article_button:
            self.parser = ArticleParser()

    def process_text(self):
        url = self.url_input.text()

        if not self.parser:
            self.text_output.setPlainText("Будь ласка, оберіть тип парсера.")
            return

        text = self.parser.extract_content(url)
        lng = "ukrainian" if self.language == "uk" else "english"
        stop_words = set(stopwords.words(lng))
        text = re.sub(r'[^\w\s]', '', text)
        tokens = word_tokenize(text.strip())
        tokens = [word for word in tokens if word not in stop_words]
        text = ' '.join(tokens)
        print(text)
        self.text_output.setPlainText(text.strip())

        if not self.nlp:
            self.setup_nlp()

        doc = self.nlp(text)

        entity_counts = Counter()
        for ent in doc.ents:
            entity_type = ent.type
            entity_counts[entity_type] += 1

        print(entity_counts.items())
        print(entity_counts.total())

        if entity_counts.total() > 0:
            self.update_pie_chart(entity_counts)

        entities = []
        for ent in doc.ents:
            entities.append(f"{ent.text} - {ent.type}")

        self.entities_output.setPlainText('\n'.join(entities))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NERApp()
    sys.exit(app.exec_())
