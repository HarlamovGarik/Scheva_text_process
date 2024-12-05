from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
from transformers import T5ForConditionalGeneration, T5Tokenizer


class UkrainianLexRankSummarizer:
    def __init__(self):
        self.summarizer = LexRankSummarizer()

    def summarize(self, text, sentences_count=3):
        parser = PlaintextParser.from_string(text, Tokenizer('ukrainian'))
        summary_sentences = self.summarizer(parser.document, sentences_count)
        summary = ' '.join(str(sentence) for sentence in summary_sentences)
        return summary


class UkrainianMT5Summarizer:

    def __init__(self):
        self.model_name = 'google/mt5-small'
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)

    def summarize(self, text, max_length=150, min_length=40):
        input_ids = self.tokenizer.encode(text, return_tensors='pt', truncation=True)
        summary_ids = self.model.generate(input_ids, max_length=max_length, min_length=min_length, length_penalty=2.0,
                                          num_beams=4, early_stopping=True)
        summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary


class T5Summarizer:
    def __init__(self, model_name="t5-small"):
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)

    def summarize(self, text, max_length=150, min_length=40):
        input_text = f"summarize: {text}"
        inputs = self.tokenizer.encode(input_text, return_tensors="pt", truncation=True)
        summary_ids = self.model.generate(
            inputs, max_length=max_length, min_length=min_length, length_penalty=2.0, num_beams=4, early_stopping=True
        )
        return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)


class TextRankSummarizerWrapper:
    def __init__(self):
        self.summarizer = TextRankSummarizer()

    def summarize(self, text, sentence_count=5):
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summary = self.summarizer(parser.document, sentence_count)
        return " ".join([str(sentence) for sentence in summary])


class PipelineSummarizer:
    def __init__(self, model_name):
        self.summarizer = pipeline("summarization", model=model_name)

    def summarize(self, text, max_length=150, min_length=40):
        summary = self.summarizer(
            text, max_length=max_length, min_length=min_length, do_sample=False
        )
        return summary[0]['summary_text']


class LexRankSummarizerWrapper:
    def __init__(self):
        self.summarizer = LexRankSummarizer()

    def summarize(self, text, sentence_count=5):
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summary = self.summarizer(parser.document, sentence_count)
        return " ".join([str(sentence) for sentence in summary])

# Використання:
# lexrank_summarizer = LexRankSummarizerWrapper()
# summary = lexrank_summarizer.summarize("Your long text here.")

# # Приклад використання
# summarizer_english = TextSummarizer("facebook/bart-large-cnn")
# english_summary = summarizer_english.summarize("Breaking news: the economy is booming, but challenges remain!")
#
# summarizer_ukrainian = TextSummarizer("Helsinki-NLP/opus-mt-en-uk")
# ukrainian_summary = summarizer_ukrainian.summarize("Новини: економіка зростає, але залишаються виклики.")
#
# print(english_summary)
# print(ukrainian_summary)
#
# # Збереження в output
# with open("output/abstract_summarization_english.txt", "w") as f:
#     f.write(english_summary)
# with open("output/abstract_summarization_ukrainian.txt", "w") as f:
#     f.write(ukrainian_summary)
