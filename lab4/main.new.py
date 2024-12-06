import os
import re
import string
import pandas as pd
from google_play_scraper import reviews, search, Sort

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split

from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier


class AppReviewProcessor:
    def __init__(self, app_name_or_url, output_dir='../output'):
        self.app_name_or_url = app_name_or_url
        self.output_dir = output_dir
        self.corpus_dir = os.path.join(self.output_dir, 'corpus')
        self.result_dir = os.path.join(self.output_dir, 'result')

        self.padding = "#" * 20
        self.ensure_directories()
        self.app_id = None
        self.data = []
        self.vectorizer = None

    def ensure_directories(self):
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.corpus_dir, exist_ok=True)
        os.makedirs(self.result_dir, exist_ok=True)

    def get_app_id(self):
        match = re.search(r'id=([\w\.]+)', self.app_name_or_url)
        if match:
            self.app_id = match.group(1)
        else:
            results = search(self.app_name_or_url, lang='en', country='us', n=1)
            if results:
                self.app_id = results[0]['appId']
            else:
                print("Застосунок не знайдено.")
                self.app_id = None

    def fetch_reviews(self, count=500):
        if not self.app_id:
            self.get_app_id()
        if not self.app_id:
            raise ValueError("Не вдалося отримати ID застосунку.")
        user_reviews, _ = reviews(
            self.app_id,
            lang='en',
            country='us',
            sort=Sort.MOST_RELEVANT,
            count=count
        )
        for review_item in user_reviews:
            filename = str(review_item['userName']).lower().replace(' ', '_')
            content = review_item['content']
            score = review_item['score']
            self.data.append(
                {
                    'filename': filename,
                    'text': content,
                    'score': score
                }
            )

    def preprocess_text(self, text):
        stop_words = set(stopwords.words('english'))
        text = re.sub(r'[^\w\s]', '', text)                 # Видаляємо розділові знаки
        text = re.sub(r'\d+', '', text)                     # Видаляємо цифри
        tokens = word_tokenize(text.lower())                            # Переводимо в нижній регістр
        tokens = [word for word in tokens if word not in stop_words]    # Видали в нижній регістр
        return ' '.join(tokens)

    def save_corpus(self):
        # Зберігаємо кожен документ в окремий .txt файл у директорії corpus
        for item in self.data:
            filename = item['filename']
            filename = re.sub(rf'[{re.escape(string.punctuation)}]', '', filename)
            filename += "_"+str(item['score'])+"_"
            filename += ".txt"

            filepath = os.path.join(self.corpus_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(item['text'])

    def prepare_data(self):
        # Попередня обробка текстів
        for i, item in enumerate(self.data):
            self.data[i]['text'] = self.preprocess_text(item['text'])

        # Створення матриці ознак
        self.vectorizer = CountVectorizer()
        X = self.vectorizer.fit_transform([d['text'] for d in self.data])
        y = [0 if d['score'] <= 3 else 1 for d in self.data]
        return X, y

    def split_data(self, X, y, test_size=0.2, random_state=42):
        return train_test_split(X, y, test_size=test_size, random_state=random_state)

    def naive_bayes_result(self, X_train, X_test, y_train, y_test):
        #################################
        ######### Наївний Байєс #########
        #################################

        nb_model = MultinomialNB()
        nb_model.fit(X_train, y_train)
        y_pred_nb = nb_model.predict(X_test)

        nb_result = classification_report(y_test, y_pred_nb)
        nb_acc = accuracy_score(y_test, y_pred_nb)

        print(f"\n{self.padding}###############{self.padding}")
        print(f"{self.padding} Наївний Байєс {self.padding}")
        print(f"{self.padding}###############{self.padding}\n")
        print(nb_result)
        print("Наївний Байєс - Точність:", nb_acc)

        return nb_acc


    def logistic_regression_result(self, X_train, X_test, y_train, y_test):
        #################################
        ###### Логістична регресія ######
        #################################

        lr_model = LogisticRegression(max_iter=1000)
        lr_model.fit(X_train, y_train)
        y_pred_lr = lr_model.predict(X_test)

        lr_report = classification_report(y_test, y_pred_lr)
        lr_acc = accuracy_score(y_test, y_pred_lr)

        print(f"\n{self.padding}#####################{self.padding}")
        print(f"{self.padding} Логістична регресія {self.padding}")
        print(f"{self.padding}#####################{self.padding}\n")
        print(lr_report)
        print("Логістична регресія - Точність:", lr_acc)

        return lr_acc


    def knn_result(self, X_train, X_test, y_train, y_test, metric='euclidean', n=3):
        knn_model = KNeighborsClassifier(n_neighbors=n, metric=metric)
        knn_model.fit(X_train, y_train)
        y_pred_knn = knn_model.predict(X_test)

        knn_report = classification_report(y_test, y_pred_knn)
        knn_acc = accuracy_score(y_test, y_pred_knn)
        metric_title = str(metric).capitalize()

        print(f"\n{self.padding}#############################{self.padding}")
        print(f"{self.padding} KNN (k={n}, metric={metric_title}) {self.padding}")
        print(f"{self.padding}#############################{self.padding}\n")
        print(knn_report)
        print(f"{metric_title} k={n} - Точність:", knn_acc)

        return knn_acc


    def train_and_evaluate_models(self, X_train, X_test, y_train, y_test):
        results = []

        nb_acc = self.naive_bayes_result(X_train, X_test, y_train, y_test)
        results.append(['Naive Bayes', nb_acc])

        lr_acc = self.logistic_regression_result(X_train, X_test, y_train, y_test)
        results.append(['Logistic Regression', lr_acc])

        knn_acc_3_euclidean = self.knn_result(X_train, X_test, y_train, y_test, metric='euclidean', n=3)
        results.append(['KNN (k=3, Euclidean)', knn_acc_3_euclidean])

        knn_acc_5_euclidean = self.knn_result(X_train, X_test, y_train, y_test, metric='euclidean', n=5)
        results.append(['KNN (k=5, Euclidean)', knn_acc_5_euclidean])

        knn_acc_3_manhattan = self.knn_result(X_train, X_test, y_train, y_test, metric='manhattan', n=3)
        results.append(['KNN (k=3, Manhattan)', knn_acc_3_manhattan])

        knn_acc_5_manhattan = self.knn_result(X_train, X_test, y_train, y_test, metric='manhattan', n=5)
        results.append(['KNN (k=5, Manhattan)', knn_acc_5_manhattan])

        # Збереження результатів
        results_df = pd.DataFrame(results, columns=["Model", "Accuracy"])
        results_df.to_csv(os.path.join(self.result_dir, "model_results.csv"), index=False)

        # Повертаємо для можливого додаткового використання
        return results_df

    def save_train_test_split(self, X_train, X_test, y_train, y_test):
        # Збережемо навчальну та тестову вибірки у CSV
        # Перетворимо у звичайну матрицю та збережемо
        train_df = pd.DataFrame(X_train.toarray(), columns=self.vectorizer.get_feature_names_out())
        train_df['label'] = y_train
        train_df.to_csv(os.path.join(self.result_dir, 'train_data.csv'), index=False)

        test_df = pd.DataFrame(X_test.toarray(), columns=self.vectorizer.get_feature_names_out())
        test_df['label'] = y_test
        test_df.to_csv(os.path.join(self.result_dir, 'test_data.csv'), index=False)


if __name__ == '__main__':
    app_name_or_url = input("Введіть Google Play ID або назву додатку: ")
    processor = AppReviewProcessor(app_name_or_url=app_name_or_url)
    processor.fetch_reviews(count=500)
    # processor.save_corpus()

    X, y = processor.prepare_data()
    X_train, X_test, y_train, y_test = processor.split_data(X, y)
    processor.save_train_test_split(X_train, X_test, y_train, y_test)
    results_df = processor.train_and_evaluate_models(X_train, X_test, y_train, y_test)

    print("\nРезультати навчання моделей:")
    print(results_df)