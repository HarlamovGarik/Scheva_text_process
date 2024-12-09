from transformers import pipeline
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer


class PipelineSummarizer:
    def __init__(self, model_name):
        self.summarizer = pipeline("summarization", model=model_name)

    def summarize(self, text,
                  max_length=300,
                  min_length=100,
                  num_beams=3,
                  early_stopping=True
                  ):
        summary = self.summarizer(
            text,
            max_length=max_length,
            min_length=min_length,
            do_sample=False,
            num_beams=num_beams,
            early_stopping=early_stopping,
        )
        return summary[0]['summary_text']


class TextRankSummarizerWrapper:
    def __init__(self, sentence_count=10):
        self.summarizer = TextRankSummarizer()
        print(self.summarizer)
        self.sentence_count = sentence_count

    def summarize(self, text, language="en"):
        language = "english" if language == "en" else "ukrainian"
        parser = PlaintextParser.from_string(text, Tokenizer(language))
        summary = self.summarizer(parser.document, self.sentence_count)
        return " ".join([str(sentence) for sentence in summary])


class LexRankSummarizerWrapper:
    def __init__(self, sentence_count=10):
        self.summarizer = LexRankSummarizer()
        print(self.summarizer)
        self.sentence_count = sentence_count

    def summarize(self, text, language="en", ):
        language = "english" if language == "en" else "ukrainian"
        parser = PlaintextParser.from_string(text, Tokenizer(language))
        summary = self.summarizer(parser.document, self.sentence_count)
        return " ".join([str(sentence) for sentence in summary])
