import re
import string

import pymorphy2

import spacy
import stanza
from nltk import word_tokenize
from nltk.corpus import stopwords
from lab5.parser import NewsParser

content_parser = NewsParser()
url = "https://www.unian.ua/war/masovana-ataka-rf-rosiyani-vdarili-kalibrami-z-kasetnimi-boyepripasami-zelenskiy-12834579.html"

text = content_parser.extract_content(url)
text = re.sub(r'[^\w\s],.', '', text)
text = re.sub(rf'[{re.escape(string.punctuation)}]', '', text)

print(text)
stop_words = set(stopwords.words("ukrainian"))
# tokens = word_tokenize(text.strip())
tokens = text.split(" ")
morph = pymorphy2.MorphAnalyzer(lang="uk")

tokens = [morph.parse(word)[0].normal_form for word in tokens if word not in stop_words]
print(tokens)
text = " ".join(tokens)

nlp = stanza.Pipeline("uk", processors='tokenize,ner', verbose=False)
doc = nlp(text)

entities = [(ent.text, ent.type) for ent in doc.ents]
print(entities)