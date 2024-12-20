import stanza

# Ініціалізація моделі для української мови
stanza.download('uk')
nlp = stanza.Pipeline('uk', processors='tokenize,ner')

# Текст для аналізу
text = """
На третьому році повномасштабної війни частина українського суспільства прийшла до важливого щабля самоусвідомлення — знову? знову! — а саме до життєвої потреби внутрішніх змін, без яких ми можемо приректи себе на поразку. Знову? Знову! Сьогодні це привід запитати себе: а що з нашою армією не так і як саме ми її зміцнюємо зсередини?
Зміни в українських Силах Оборони відбуваються вже десять років, втім недостатньо швидко, щоб ситуація змінилась кардинально. Під час повномасштабної війни вони прискорились, але з’явився спротив під гаслом «під час війни реформи не на часі». В своєму подкасті активіст та волонтер Сергій Стерненко сказав:
«В нас катастрофічна проблема з організаційною структурою ЗСУ. Ця проблема може призвести до абсолютно неконтрольованої масштабної кризи стратегічного рівня і спричинити абсолютний колапс з подальшою втратою української державності. Чим більше часу минає і чим менше відбувається дійсно якісних реформ всередині війська, тим вища ймовірність того, що нам хана».
"""

# 1) Ручна розмітка тексту (еталон)
# Створимо список еталонних іменованих сутностей у форматі (текст, тип, початковий індекс, кінцевий індекс)
manual_entities = [
    ("українського суспільства", "ORG"),
    ("Силах Оборони", "ORG"),
    ("Сергій Стерненко", "PER"),
    ("ЗСУ", "ORG"),
    ("української державності", "LOC"),
]

# 2) Отримання прогнозу моделі
doc = nlp(text)
predicted_entities = []
for ent in doc.ents:
    predicted_entities.append((ent.text, ent.type, ent.start_char, ent.end_char))

TP = 0  # Кількість правильно передбачених сутностей
FP = 0  # Кількість неправильно передбачених сутностей (яких немає в еталоні)
FN = 0  # Кількість сутностей, які модель пропустила

manual_entities_set = set([(ent[0], ent[1]) for ent in manual_entities])
predicted_entities_set = set([(ent[0], ent[1]) for ent in predicted_entities])

TP = len(manual_entities_set & predicted_entities_set)

FP = len(predicted_entities_set - manual_entities_set)

FN = len(manual_entities_set - predicted_entities_set)

if TP + FP > 0:
    Precision = TP / (TP + FP)
else:
    Precision = 0

if TP + FN > 0:
    Recall = TP / (TP + FN)
else:
    Recall = 0

if Precision + Recall > 0:
    F1 = 2 * (Precision * Recall) / (Precision + Recall)
else:
    F1 = 0

print(f"TP (True Positive): {TP}")
print(f"FP (False Positive): {FP}")
print(f"FN (False Negative): {FN}")
print(f"Precision: {Precision:.2f}")
print(f"Recall: {Recall:.2f}")
print(f"F1-score: {F1:.2f}")
