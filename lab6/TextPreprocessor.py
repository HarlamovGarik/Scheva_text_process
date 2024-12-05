import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

class TextPreprocessor:
    def __init__(self, language='english'):
        self.language = language
        self.stop_words = stopwords.words(language)
        self.lemmatizer = WordNetLemmatizer() if language == 'english' else None
        self.stemmer = SnowballStemmer(language) if language in ['english', 'russian', 'ukrainian'] else None

    def preprocess(self, text):
        text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
        text = text.lower()  # Convert to lowercase
        words = word_tokenize(text)
        words = [word for word in words if word not in self.stop_words]
        if self.lemmatizer:
            words = [self.lemmatizer.lemmatize(word) for word in words]
        elif self.stemmer:
            words = [self.stemmer.stem(word) for word in words]
        return ' '.join(words)

# Приклад використання
preprocessor = TextPreprocessor(language='english')
processed_text = preprocessor.preprocess("Breaking news: the economy is booming, but challenges remain!")
print(processed_text)
