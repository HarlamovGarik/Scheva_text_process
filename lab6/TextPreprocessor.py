import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer

# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('wordnet')

class TextPreprocessor:
    def __init__(self, language='english'):
        self.language = language
        self.stop_words = stopwords.words(language)
        self.lemmatizer = WordNetLemmatizer() if language == 'english' else None
        self.stemmer = SnowballStemmer(language) if language in ['english', 'ukrainian'] else None

    def preprocess_sentence(self, sentence):
        sentence = re.sub(r'[^\w\s]', '', sentence)
        sentence = sentence.lower()
        words = word_tokenize(sentence)
        words = [word for word in words if word not in self.stop_words]
        if self.lemmatizer:
            words = [self.lemmatizer.lemmatize(word) for word in words]
        elif self.stemmer:
            words = [self.stemmer.stem(word) for word in words]
        return ' '.join(words)

    def preprocess(self, text):
        sentences = sent_tokenize(text)
        processed_sentences = [self.preprocess_sentence(sentence) for sentence in sentences]
        return ' '.join(processed_sentences)
