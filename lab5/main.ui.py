import re
import string
import sys
from collections import Counter

import pymorphy2
import stanza
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import spacy

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QSizePolicy,
    QButtonGroup, QRadioButton, QGroupBox, QApplication, QCheckBox
)

from lab5.utils.ChartDialog import ChartDialog
from lab5.utils.BaseWindow import BaseWindow
from lab5.parser import ScenarioParser, NewsParser, ArticleParser, Parser
from lab5.utils.LoadingDialog import is_model_downloaded, LoadingDialog, DownloadModelThread, DownloadSpacyModelThread
from lab5.utils.Timer import Timer


class MainWindow(BaseWindow):
    def __init__(self):
        super().__init__(900, 600, 'NER: Lab5')
        self.left_layout = None
        self.content_parser = Parser()
        self.nlp_models = {}
        self.nlp = None
        self.language = 'uk'  # Default language
        self.model = 'stanza'  # Default model

        self.preprocessing_options = {
            "lowercase": {
                "label": "Перевести в нижній регістр",
                "checked": False
            },
            "remove_stopwords": {
                "label": "Прибрати StopWords",
                "checked": False
            },
            "remove_punctuation": {
                "label": "Прибрати розділові знаки",
                "checked": False
            },
            "use_morph_analysis": {
                "label": "Використати морфологічний аналіз",
                "checked": False
            }
        }

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        self.setup_form(main_layout)
        self.setup_output_text(main_layout)
        self.show()

    def setup_form(self, main_layout):
        left_widget = QWidget()
        self.left_layout = QVBoxLayout()
        left_widget.setLayout(self.left_layout)

        left_widget.setMinimumSize(300, 400)
        left_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.setup_models_groupbox()
        self.setup_languages_groupbox()
        self.setup_site_groupbox()
        self.setup_input_groupbox()
        self.setup_text_preprocess_configuration()

        main_layout.addWidget(left_widget)

    def setup_text_preprocess_configuration(self):
        preprocess_groupbox = QGroupBox("Налаштування")
        preprocess_layout = QVBoxLayout()
        preprocess_groupbox.setLayout(preprocess_layout)

        self.preprocess_button_group = QButtonGroup(self)
        self.preprocess_button_group.setExclusive(False)  # Allow multiple checkboxes to be checked

        self.create_preprocessing_checkboxes(preprocess_layout)
        self.preprocess_button_group.buttonClicked.connect(self.on_preprocessing_option_changed)

        self.left_layout.addWidget(preprocess_groupbox)

    def create_preprocessing_checkboxes(self, layout):
        for key, value in self.preprocessing_options.items():
            checkbox = QCheckBox(value["label"])
            checkbox.setChecked(value["checked"])
            checkbox.setObjectName(key)
            self.preprocess_button_group.addButton(checkbox)
            layout.addWidget(checkbox)

    def on_preprocessing_option_changed(self, button):
        key = button.objectName()
        if key in self.preprocessing_options:
            self.preprocessing_options[key]["checked"] = button.isChecked()
            print(f"Updated {key}: {self.preprocessing_options[key]['checked']}")

    def setup_models_groupbox(self):
        models_groupbox = QGroupBox("Моделі")
        models_layout = QVBoxLayout()
        models_groupbox.setLayout(models_layout)

        self.model_group = QButtonGroup(self)
        self.stanza_button = QRadioButton("Stanza")
        self.eng_core_button = QRadioButton("Eng Core")

        self.model_group.addButton(self.stanza_button)
        self.model_group.addButton(self.eng_core_button)

        # Set default selection
        self.stanza_button.setChecked(True)
        self.model = 'stanza'  # Default model

        # Connect signal for model selection change
        self.model_group.buttonClicked.connect(self.setup_nlp)

        models_layout.addWidget(self.stanza_button)
        models_layout.addWidget(self.eng_core_button)
        self.left_layout.addWidget(models_groupbox)

    def setup_languages_groupbox(self):
        languages_groupbox = QGroupBox("Підтримувані мови")
        languages_layout = QVBoxLayout()
        languages_groupbox.setLayout(languages_layout)

        self.language_group = QButtonGroup(self)
        self.ukrainian_button = QRadioButton("Українська")
        self.english_button = QRadioButton("Англійська")

        self.language_group.addButton(self.ukrainian_button)
        self.language_group.addButton(self.english_button)

        # Set default selection
        self.ukrainian_button.setChecked(True)
        self.language = 'uk'  # Default language

        # Connect signal for language selection change
        self.language_group.buttonClicked.connect(self.change_language)

        languages_layout.addWidget(self.ukrainian_button)
        languages_layout.addWidget(self.english_button)
        self.left_layout.addWidget(languages_groupbox)

    def setup_site_groupbox(self):
        site_groupbox = QGroupBox("Тип сайту")
        site_layout = QVBoxLayout()
        site_groupbox.setLayout(site_layout)

        self.site_group = QButtonGroup(self)
        self.scenario_button = QRadioButton("Сценарії")
        self.news_button = QRadioButton("Новини")
        self.article_button = QRadioButton("Наукова стаття")

        self.site_group.addButton(self.scenario_button)
        self.site_group.addButton(self.news_button)
        self.site_group.addButton(self.article_button)

        # Set default selection
        self.news_button.setChecked(True)
        self.content_parser = NewsParser()  # Default site type

        # Connect signal for site type selection change
        self.site_group.buttonClicked.connect(self.change_site_type)

        site_layout.addWidget(self.scenario_button)
        site_layout.addWidget(self.news_button)
        site_layout.addWidget(self.article_button)
        self.left_layout.addWidget(site_groupbox)

    def setup_input_groupbox(self):
        input_groupbox = QGroupBox("Ввід")
        input_layout = QVBoxLayout()
        input_groupbox.setLayout(input_layout)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Введіть URL")
        self.process_button = QPushButton("Обробити")
        self.process_button.clicked.connect(self.process_text)

        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.process_button)
        self.left_layout.addWidget(input_groupbox)

    def setup_output_text(self, main_layout):
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        # Output text field
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)

        # Found named entities field
        self.entities_output = QTextEdit()
        self.entities_output.setReadOnly(True)

        right_layout.addWidget(QLabel("Вилучений текст:"))
        right_layout.addWidget(self.text_output)
        right_layout.addWidget(QLabel("Знайдені іменовані сутності:"))
        right_layout.addWidget(self.entities_output)

        # Set size policy
        right_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add right widget to main layout
        main_layout.addWidget(right_widget)

    def setup_nlp(self):
        selected_button = self.model_group.checkedButton()
        if selected_button == self.stanza_button:
            self.model = 'stanza'
            # Enable both language options
            self.ukrainian_button.setEnabled(True)
            self.english_button.setEnabled(True)
        elif selected_button == self.eng_core_button:
            self.model = 'eng_core'
            # Only English is supported
            self.ukrainian_button.setEnabled(False)
            self.english_button.setEnabled(True)
            self.english_button.setChecked(True)
            self.language = 'en'

        if self.model == 'stanza':
            if not is_model_downloaded(self.language):
                # Show loading dialog
                loading_dialog = LoadingDialog(self,
                                               message=f"Завантаження моделі для мови '{self.language}', будь ласка, зачекайте...")
                loading_dialog.exec_()
                QApplication.processEvents()
                # Start download in separate thread
                self.download_thread = DownloadModelThread(self.language)
                self.download_thread.finished.connect(loading_dialog.close)
                self.download_thread.start()
                self.download_thread.wait()
            # Load stanza model
            self.nlp = stanza.Pipeline(self.language, processors='tokenize,ner', verbose=False)
        elif self.model == 'eng_core':
            try:
                self.nlp = spacy.load('en_core_web_sm')
            except OSError:
                # Show loading dialog
                loading_dialog = LoadingDialog(self,
                                               message="Завантаження моделі 'en_core_web_sm', будь ласка, зачекайте...")
                loading_dialog.exec_()
                QApplication.processEvents()
                # Start download in separate thread
                self.download_thread = DownloadSpacyModelThread('en_core_web_sm')
                self.download_thread.finished.connect(loading_dialog.close)
                self.download_thread.start()
                self.download_thread.wait()
                # Load the model after downloading
                self.nlp = spacy.load('en_core_web_sm')
        # Cache the model
        self.nlp_models[self.language] = self.nlp

    def change_language(self):
        selected_button = self.language_group.checkedButton()
        if selected_button == self.ukrainian_button:
            self.language = 'uk'
        elif selected_button == self.english_button:
            self.language = 'en'
        self.nlp = None

    def change_site_type(self):
        selected_button = self.site_group.checkedButton()
        if selected_button == self.scenario_button:
            self.content_parser = ScenarioParser()
        elif selected_button == self.news_button:
            self.content_parser = NewsParser()
        elif selected_button == self.article_button:
            self.content_parser = ArticleParser()

    def text_analysis(self, text: str):
        if len(text) >= 2000:
            pass



    def process_text(self):
        url = self.url_input.text()
        print(url)

        if not self.content_parser:
            self.text_output.setPlainText("Будь ласка, оберіть тип парсера.")
            return
        else:
            print(self.content_parser)

        timer = Timer()
        timer.measure()
        text = self.content_parser.extract_content(url)

        print(f"Збір тексту зайняв: {timer.measure(False)}.6f секунд")

        timer.measure()

        text = text.replace("&nbsp;", " ")
        text = re.sub(r'[\n\t]', ' ', text)

        if self.preprocessing_options["lowercase"]["checked"]:
            text = text.lower()

        if self.preprocessing_options["remove_punctuation"]["checked"]:
            text = re.sub(rf'[{re.escape(string.punctuation)}]', '', text)
        else:
            text = re.sub(r'[^\w\s,.]', '', text)

        tokens = word_tokenize(text.strip())
        if self.preprocessing_options["remove_stopwords"]["checked"]:
            lng = "ukrainian" if self.language == "uk" else "english"
            stop_words = set(stopwords.words(lng))
            tokens = [word for word in tokens if word not in stop_words]
        else:
            tokens = [word for word in tokens]



        if self.preprocessing_options["use_morph_analysis"]["checked"]:
            morph = pymorphy2.MorphAnalyzer(lang=self.language)
            tokens = [morph.parse(word)[0].normal_form for word in tokens]

        text = ' '.join(tokens)
        print(tokens)

        print(f"Обробка тексту зайняла: {timer.measure(False)}.6f секунд")

        self.text_output.setPlainText(text.strip())

        if not self.nlp:
            self.setup_nlp()

        timer.measure()
        doc = self.nlp(text)
        print(f"Пошук імених сутностей зайняв: {timer.measure(False)}.6f секунд")
        entity_counts = Counter()
        entities = []

        if self.model == 'stanza':
            for ent in doc.ents:
                entity_type = ent.type
                entity_counts[entity_type] += 1
                entities.append(f"{ent.text} - {ent.type}")
        else:
            for ent in doc.ents:
                entity_type = ent.label_
                entity_counts[entity_type] += 1
                entities.append(f"{ent.text} - {ent.label_}")

        sorted_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)

        print(sorted_entities)
        print(entity_counts.total())
        cleaned_url = url.strip("https://").strip("/")
        parts = cleaned_url.split("/")

        title = f"{parts[0]} - {parts[-1]}"
        chart = ChartDialog(title, sorted_entities, entity_counts.total(), parent=self)
        chart.show()

        self.entities_output.setPlainText('\n'.join(entities))
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
