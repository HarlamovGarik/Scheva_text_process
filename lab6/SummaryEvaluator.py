import os
import pandas as pd
import spacy
import nltk
from nltk.tokenize import sent_tokenize
import language_tool_python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import spacy_udpipe
from tokenize_uk import tokenize_sents


# nltk.download('punkt')

class SummaryEvaluator:
    def __init__(self, summary_folder="result"):
        self.summary_folder = summary_folder
        # Load English spaCy model
        self.nlp_en = spacy.load('en_core_web_lg')

        # Load Ukrainian spaCy model via spacy-udpipe
        # spacy_udpipe.download("uk")
        self.nlp_uk = spacy_udpipe.load("uk")

        # Load sentence embedding models
        self.sbert_model_en = SentenceTransformer('all-MiniLM-L6-v2')
        self.sbert_model_multi = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def check_syntactic_correctness(self, text, language='en'):
        print("Checking Syntactic Correctness")
        if language == 'en':
            language="english"
            nlp = self.nlp_en
            print("nlp eng")
        elif language == 'ua':
            nlp = self.nlp_uk
        else:
            return None  # Cannot proceed

        sentences = sent_tokenize(text, language=language) if language == 'english' else tokenize_sents(text)
        print("sentences eng")
        total_sentences = len(sentences)
        parseable_sentences = 0
        for sentence in sentences:
            doc = nlp(sentence)
            if len(doc) > 0:
                parseable_sentences += 1
        if total_sentences > 0:
            score = parseable_sentences / total_sentences
        else:
            score = 0
        return round(score, 2)

    def check_semantic_coherence(self, text, language='en'):
        print("Checking Semantic Coherence")
        if language == 'en':
            tool = language_tool_python.LanguageTool('en-US')
        elif language == 'ua':
            tool = language_tool_python.LanguageTool('uk-UA')
        else:
            return None
        matches = tool.check(text)
        num_errors = len(matches)
        num_words = len(text.split())
        if num_words > 0:
            error_rate = num_errors / num_words
            score = 1.0 - error_rate
        else:
            score = 0
        return round(score, 2)

    def check_semantic_connectedness(self, text, language='en'):
        print("Checking Semantic Connectedness")
        if language == 'en':
            language="english"
        sentences = sent_tokenize(text, language=language) if language == 'english' else tokenize_sents(text)
        total_pairs = len(sentences) - 1
        if total_pairs <= 0:
            return 1.0  # Only one sentence, consider fully connected

        if language == 'en':
            sbert_model = self.sbert_model_en
        else:
            sbert_model = self.sbert_model_multi

        embeddings = sbert_model.encode(sentences)
        similarity_scores = []
        for i in range(total_pairs):
            embedding1 = embeddings[i].reshape(1, -1)
            embedding2 = embeddings[i + 1].reshape(1, -1)
            similarity = cosine_similarity(embedding1, embedding2)[0][0]
            similarity_scores.append(similarity)
        average_similarity = sum(similarity_scores) / len(similarity_scores)
        return round(average_similarity, 2)

    def evaluate_files(self, language="en"):
        results = []
        txt_files = [f for f in os.listdir(self.summary_folder) if f.endswith('.txt')]
        for txt_file in txt_files:
            metadata = txt_file.split("_")
            filename = txt_file
            method = None

            if len(metadata) == 3:
                language = metadata[0]
                filename = metadata[1]
                method = metadata[2].split(".")[0]

            print(f"{filename}: {method}: {language}")
            file_path = os.path.join(self.summary_folder, txt_file)
            text = ""
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            # Evaluate text
            syntactic_correctness = self.check_syntactic_correctness(text, language)
            semantic_coherence = self.check_semantic_coherence(text, language)
            semantic_connectedness = self.check_semantic_connectedness(text, language)

            # Store results
            results.append({
                'file_name': filename,
                'language': language,
                'method': method,
                'syntactic_correctness': syntactic_correctness,
                'semantic_coherence': semantic_coherence,
                'semantic_connectedness': semantic_connectedness
            })

        # Create DataFrame
        df = pd.DataFrame(results)
        df.to_csv('evaluation_results.csv', index=False)
        print(df)
