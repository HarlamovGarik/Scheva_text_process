import os
from collections import Counter

import stanza
import spacy


def comparative_analysis(text, details=False):
    stanza_nlp = stanza.Pipeline('en', processors='tokenize,ner', verbose=False)
    eng_core_nlp = spacy.load('en_core_web_lg')

    stanza_doc = stanza_nlp(text)
    eng_core_doc = eng_core_nlp(text)

    entities_stanza = []
    for ent in stanza_doc.ents:
        entities_stanza.append((ent.text, ent.type, ent.start_char, ent.end_char))

    entities_spacy = []
    for ent in eng_core_doc.ents:
        entities_spacy.append((ent.text, ent.label_, ent.start_char, ent.end_char))

    def normalize_text(text: str):
        return ' '.join(text.strip().split())

    entities_stanza_set = set()
    for text, label, start, end in entities_stanza:
        entities_stanza_set.add((normalize_text(text), label))

    entities_spacy_set = set()
    for text, label, start, end in entities_spacy:
        entities_spacy_set.add((normalize_text(text), label))

    os.makedirs("../output", exist_ok=True)

    ###############
    ### STANZA ####
    ###############

    entity_counts = Counter()
    with open("../output/entities_stanza.txt", "w", encoding="utf-8") as f:
        for ent in stanza_doc.ents:
            entity_type = ent.type
            entity_counts[entity_type] += 1
            f.write(f"{ent.text} - {entity_type}\n")

    sorted_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
    print(sorted_entities)
    print(entity_counts.total())

    ##########################
    ### SPACY ENG CORE LG ####
    ##########################

    entity_counts = Counter()
    with open("../output/entities_spacy.txt", "w", encoding="utf-8") as f:
        for ent in eng_core_doc.ents:
            entity_type = ent.label_
            entity_counts[entity_type] += 1
            f.write(f"{ent.text} - {entity_type}\n")

    sorted_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
    print(sorted_entities)
    print(entity_counts.total())


    TP_set = entities_stanza_set & entities_spacy_set
    FP_set = entities_stanza_set - entities_spacy_set
    FN_set = entities_spacy_set - entities_stanza_set

    TP = len(TP_set)
    FP = len(FP_set)
    FN = len(FN_set)

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

    # Виведення результатів
    print(f"TP (True Positive): {TP}")
    print(f"FP (False Positive): {FP}")
    print(f"FN (False Negative): {FN}")
    print(f"Precision: {Precision:.2f}")
    print(f"Recall: {Recall:.2f}")
    print(f"F1-score: {F1:.2f}")

    if details:
        print("\nTrue Positives:")
        for ent in TP_set:
            print(ent)

        print("\nFalse Positives (Stanza extra entities):")
        for ent in FP_set:
            print(ent)

        print("\nFalse Negatives (Missed by Stanza):")
        for ent in FN_set:
            print(ent)


if __name__ == '__main__':
    text = """ 
    What happening northwestern Syria Reuters HTS allies said launched offensive “ deter aggression ” government Rebel forces launched largest offensive Syrian government years They captured swathe land across northwest country including second city Aleppo Syrian military rapidly withdrew troops The rebels battling military near central city Hama government ’ key ally Russia carrying air strikes Why war Syria A peaceful prodemocracy uprising Syrian President Bashar alAssad 2011 turned fullscale civil war devastated country drawn regional world powers More half million people killed 12 million forced flee homes five million refugees asylum seekers abroad Prior rebels ’ offensive war felt effectively Assad ’ government regained control cities help Russia Iran Iranianbacked militias However large parts country remain government ’ direct control These include northern eastern areas controlled Kurdishled alliance armed groups supported United States The rebels ’ last remaining stronghold northwestern provinces Aleppo Idlib border Turkey home four million people many displaced The northwest dominated Islamist militant group Hayat Tahrir alSham HTS Turkishbacked rebel factions known Syrian National Army SNA also control territory support Turkish troops What Hayat Tahrir alSham HTS set 2012 different name alNusra Front pledged allegiance alQaeda following year AlNusra Front regarded one effective deadly groups ranged President Assad But jihadist ideology appeared driving force rather revolutionary zeal seen time odds main rebel coalition known Free Syrian Army In 2016 AlNusra broke ties alQaeda took name Hayat Tahrir alSham merged factions year later However UN US UK number countries continue consider HTS alQaeda affiliate frequently refer alNusra Front HTS consolidated power Idlib Aleppo provinces crushing rivals including alQaeda Islamic State IS group cells set socalled Syrian Salvation Government administer territory The eventual goal HTS topple Assad establish form Islamic governance But shown little sign attempting reignite conflict major scale renew challenge Assad ’ rule Inside Aleppo Family reunions nervousness rebel rule fear war Bowen Syrias rebel offensive astonishing dont write Assad Reuters Syrian Russian warplanes bombed rebelheld areas including city Idlib response offensive Why rebels launch offensive For several years Idlib remained battleground Syrian government forces tried regain control But 2020 Turkey Russia brokered ceasefire halt push government retake Idlib The ceasefire largely held despite sporadic fighting In October UN special envoy Syria said HTS carried significant raid governmentheld areas Russia resumed air strikes first time months progovernment forces significantly accelerated drone strikes shelling On Wednesday HTS allied groups said launched offensive “ deter aggression ” accusing government allied Iranbacked militias escalation northwest But came time Syrian government allies preoccupied conflicts The Iranbacked Lebanese group Hezbollah crucial helping Assad push back rebels early years war suffered recently Israel ’ offensive Lebanon Israeli strikes eliminated Iranian military commanders Syria degraded supply lines progovernment militias Russia also distracted war Ukraine Without Assad ’ forces left exposed How government allies responded President Assad vowed “ crush ” rebels referring “ terrorists ” In call Iranian counterpart Massoud Pezeshkian Monday blamed US Western countries offensive saying trying “ redraw map ” region Pezeshkian emphasised Iran stood “ firmly alongside Syrian government people ” preserving Syria ’ sovereignty territorial integrity cornerstone regional strategy Kremlin spokesman Dmitry Peskov said Russia also considered situation around Aleppo “ attack Syrian sovereignty ” ” favour Syrian authorities bringing order area restoring constitutional order soon possible ” EPA Irans Foreign Minister Abbas Araqchi L assured President Bashar alAssad R Tehrans continuing support What Western powers Turkey saying The US UK France Germany opposed Assad issued joint statement Monday urged “ deescalation parties protection civilians infrastructure prevent displacement disruption humanitarian access ” They also called “ Syrianled political solution conflict ” outlined 2015 UN Security Council resolution On Saturday White House National Security Council spokesman Sean Savett said Assad ’ refusal engage political process “ reliance Russia Iran ” created conditions unfolding ” He also insisted “ United States nothing offensive ” Turkey ’ Foreign Minister Hakan Fidan also said “ would mistake time try explain events Syria foreign interference ” called Syrian government “ reconcile people legitimate opposition ” Middle East Syrian civil war Syria
    """
    comparative_analysis(text)