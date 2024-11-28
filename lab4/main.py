import os
import re
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

# nltk.download('punkt_tab')
# nltk.download('stopwords')

from google_play_scraper import reviews, search, Sort

def get_app_id(app_name_or_url):
    # Якщо це URL, витягуємо app ID
    match = re.search(r'id=([\w\.]+)', app_name_or_url)
    if match:
        return match.group(1)
    else:
        results = search(app_name_or_url, lang='en', country='us', n=1)
        if results:
            return results[0]['appId']
        else:
            print("Застосунок не знайдено.")
            return None

app_name_or_url = input("Введіть Google Play ID: ")
app_id = get_app_id(app_name_or_url)
user_reviews, _ = reviews(
    app_id,
    lang='en',
    country='us',
    sort=Sort.MOST_RELEVANT,
    count=500
)
print(len(user_reviews))
data = []

for review in user_reviews:
    data.append(
        {
            'filename': str(review['userName']).lower().replace(' ', '_').replace(' ', '_'),
            'text': review['content'],
            'score': review['score']
        }
    )


# Завантаження даних
def load_text_files(folder_path):
    files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    data = []
    for file in files:
        with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as f:
            data.append({"text": f.read(), "filename": file})
    return data

# Попередня обробка тексту
def preprocess_text(data):
    print(f"Process file - {data["filename"]}")
    text = data['text']
    stop_words = set(stopwords.words('english'))

    text = re.sub(r'[^\w\s]', '', text)  # Видаляємо розділові знаки
    text = re.sub(r'\d+', '', text)  # Видаляємо цифри

    tokens = word_tokenize(text.lower())  # Токенізація і приведення до нижнього регістру
    tokens = [word for word in tokens if word not in stop_words]  # Видаляємо стоп-слова
    tokens = ' '.join(tokens)
    data['text'] = tokens
    return data


# folder_path = "../assets/reviews"
# data = load_text_files(folder_path)

preprocess_data = [preprocess_text(item) for item in data]

preprocess_text = [item["text"] for item in preprocess_data]

vectorizer = CountVectorizer()
X = vectorizer.fit_transform(preprocess_text)  # Матриця частот слів
df_bow = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out())

labels = [0 if item['score'] <= 3 else 1 for item in data]
y = labels

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score

nb_model = MultinomialNB()
nb_model.fit(X_train, y_train)

# Прогнозування
y_pred_nb = nb_model.predict(X_test)

# Оцінка
print("Наївний Байєс:")
print(classification_report(y_test, y_pred_nb))
print("Точність:", accuracy_score(y_test, y_pred_nb))

from sklearn.linear_model import LogisticRegression

# Навчання моделі
lr_model = LogisticRegression()
lr_model.fit(X_train, y_train)

# Прогнозування
y_pred_lr = lr_model.predict(X_test)

# Оцінка
print("Логістична регресія:")
print(classification_report(y_test, y_pred_lr))
print("Точність:", accuracy_score(y_test, y_pred_lr))

from sklearn.neighbors import KNeighborsClassifier

# Навчання моделі (k=3)
knn_model_3 = KNeighborsClassifier(n_neighbors=3, metric='euclidean')
knn_model_3.fit(X_train, y_train)
y_pred_knn_3 = knn_model_3.predict(X_test)

# Навчання моделі (k=5)
knn_model_5 = KNeighborsClassifier(n_neighbors=5, metric='manhattan')
knn_model_5.fit(X_train, y_train)
y_pred_knn_5 = knn_model_5.predict(X_test)

# Оцінка
print("KNN (k=3, Euclidean):")
print(classification_report(y_test, y_pred_knn_3))
print("Точність:", accuracy_score(y_test, y_pred_knn_3))

print("KNN (k=5, Manhattan):")
print(classification_report(y_test, y_pred_knn_5))
print("Точність:", accuracy_score(y_test, y_pred_knn_5))
