from lab5.parser import NewsParser
from lab6.PipelineSummarizer import PipelineSummarizer, LexRankSummarizerWrapper, T5Summarizer, TextRankSummarizerWrapper

if "__main__" == __name__:
    url = "https://www.bbc.com/news/articles/cwy5ypkn7kjo"
    newsParser = NewsParser()
    content = newsParser.extract_content(url)

    content_word_count = len(content.split())
    if content_word_count < 50:
        print("The content is too short for summarization.")
    else:
        max_length = int(content_word_count * 0.3)
        min_length = int(content_word_count * 0.1)

        summarizer_english = PipelineSummarizer("facebook/bart-large-cnn")
        t5_summarizer = T5Summarizer("t5-small")
        lexrank_summarizer = LexRankSummarizerWrapper()
        text_rank_summarizer = TextRankSummarizerWrapper()

        text_rank_summary_result = text_rank_summarizer.summarize(content, sentence_count=5)
        lexrank_summary_result = lexrank_summarizer.summarize(content, sentence_count=5)
        t5_summary_result = t5_summarizer.summarize(
            content, max_length=max_length, min_length=min_length
        )
        bart_summary_result = summarizer_english.summarize(
            content, max_length=max_length, min_length=min_length
        )

        print(t5_summary_result)
        print(lexrank_summary_result)
        print(text_rank_summary_result)
        print(bart_summary_result)
