import re
from nltk import sent_tokenize
from lab6.PipelineSummarizer import PipelineSummarizer
from lab6.SummaryEvaluator import SummaryEvaluator
from lab6.main import split_into_chunks
from lab6.parser import BookParser

if "__main__" == __name__:
    evaluator = SummaryEvaluator(summary_folder="abstract")
    evaluator.evaluate_files()


# if "__main__" == __name__:
#     files = {
#         "en": {
#             "url": "https://anylang.net/ru/books/en/ostrov-sokrovishch/read",
#             "filename": "treasure-island",
#             "title": "Robert Louis Stevenson Treasure Island",
#             "genre": "Adventure novel",
#             "specifics": "The text is rich in descriptions of adventures, naval battles, and mysteries. The style is dynamic, vivid, and features engaging dialogues. The structure revolves around treasure hunting, divided into distinct stages: the map, the journey, the discovery, and the final confrontation. It conveys an atmosphere of mystery and the romanticism of the pirate world."
#         }
#     }
#     abstract_summarizer  = PipelineSummarizer("facebook/bart-large-cnn")
#     # abstract_summarizer = PipelineSummarizer("csebuetnlp/mT5_multilingual_xlsum")
#
#     summarizers = [{
#         "name": "google-pegasus",
#         "summary": abstract_summarizer
#     }]
#
#     padd = "#" * 20
#
#     for lang, file_data in files.items():
#         title = file_data["title"]
#         filename = file_data["filename"]
#
#         print(f"Обробляємо текст для мови: {lang}")
#         parser = BookParser(language=lang, url=file_data["url"], params=file_data.get("params"))
#         content = parser.extract_content()
#
#         print(f"{padd}###########{padd}")
#         print(f"{padd} {title} {padd}")
#         print(f"{padd}###########{padd}")
#
#         content_word_count = len(content.split())
#         print(f"Word Count: {content_word_count}")
#
#         chapter_pattern = r'\d+\.\s' if lang == "en" else r'Розділ\s+[ІIVXLCDM]+'
#         chapters = re.split(chapter_pattern, content)
#
#         for summarizer in summarizers:
#             summary_list = []
#             summarizer_name = summarizer["name"]
#             summarizer_instance = summarizer["summary"]
#
#             for i, chapter in enumerate(chapters[:3], start=1):
#                 chapter = re.sub(r'\s+', ' ', chapter)
#                 content_word_count = len(chapter.split())
#
#                 print(f"{padd}###########{padd}")
#                 print(f"{padd} CHAPTER {i} {padd}")
#                 print(f"{padd}###########{padd}")
#                 chapter_summary = []
#
#                 chunks = split_into_chunks(chapter)
#                 for j, chunk in enumerate(chunks, start=1):
#                     sentences = sent_tokenize(chunk)
#                     print(f"{padd} CHUNK {j} {padd}")
#                     print(f"Кількість слів: {len(chunk.split())}")
#                     print(f"Кількість речень: {len(sentences)}")
#
#                     summary = summarizer_instance.summarize(chunk)
#
#                     chapter_summary.append(summary)
#
#                 summary_list.append("\n".join(chapter_summary))
#
#             output_filename = f"./result/{lang}_{filename}_{summarizer_name}.txt"
#             with open(output_filename, "w", encoding="utf-8") as f:
#                 for i, chapter_summary in enumerate(summary_list, start=1):
#                     print(f"CHAPTER {i} - {summarizer_name}:")
#                     print(chapter_summary + "\n")
#                     f.write(chapter_summary + "\n\n")
