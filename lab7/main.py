from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef, Literal

# Ініціалізація графу
g = Graph()

# Іменовані простори
EX = Namespace("http://example.org/ontology#")
g.bind("ex", EX)

# Додамо класи
classes = {
    "Conflict": "Основний клас, що описує конфлікт",
    "Actor": "Клас для учасників конфлікту (держави, організації, угрупування)",
    "Event": "Події, пов'язані з конфліктом",
    "Location": "Місця, де відбуваються події",
    "Outcome": "Результати конфлікту",
}

for class_name, class_description in classes.items():
    g.add((EX[class_name], RDF.type, OWL.Class))
    g.add((EX[class_name], RDFS.comment, Literal(class_description)))

# Додамо підкласи
subclasses = {
    "Actor": ["Government", "RebelGroup", "ForeignPower"],
    "Event": ["Ceasefire", "Offensive", "HumanitarianCrisis"],
    "Location": ["City", "Province"],
    "Outcome": ["Victory", "Displacement", "HumanRightsViolation"],
}

for parent, children in subclasses.items():
    for child in children:
        g.add((EX[child], RDF.type, OWL.Class))
        g.add((EX[child], RDFS.subClassOf, EX[parent]))

# Додамо об'єкти та зв'язки
instances = {
    "Aleppo": ("Location", "City"),
    "Idlib": ("Location", "Province"),
    "Hayat_Tahrir_al_Sham": ("Actor", "RebelGroup"),
    "Syrian_Government": ("Actor", "Government"),
    "Russia": ("Actor", "ForeignPower"),
    "Ceasefire_2020": ("Event", "Ceasefire"),
}

for instance, (class_name, subclass_name) in instances.items():
    g.add((EX[instance], RDF.type, EX[subclass_name]))
    g.add((EX[instance], RDFS.subClassOf, EX[class_name]))

# Додамо семантичні зв'язки
relations = {
    ("Hayat_Tahrir_al_Sham", "Aleppo"): "controls",
    ("Russia", "Ceasefire_2020"): "brokered",
    ("Syrian_Government", "Idlib"): "claims_control",
    ("Hayat_Tahrir_al_Sham", "Syrian_Government"): "opposes",
}

for (subject, obj), relation in relations.items():
    g.add((EX[subject], EX[relation], EX[obj]))

# Збережемо в OWL файл
owl_file_path = "syrian_conflict.owl"
g.serialize(destination=owl_file_path, format="xml")

print(f"OWL файл збережено: {owl_file_path}")
