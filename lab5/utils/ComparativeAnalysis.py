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
    Pariss Gothic jewel NotreDame to reopen five years after fire Getty Images The world gets a first look inside a resplendent new NotreDame on Friday , as Frances President Emmanuel Macron conducts a televised tour to mark the cathedrals imminent reopening . Fiveandahalf years after the devastating fire of 2019 , Pariss Gothic jewel has been rescued , renovated and refurbished offering visitors what promises to be a breathtaking visual treat . The president accompanied by his wife Brigitte and Archbishop of Paris Laurent Ulrich are kicking off a programme of ceremonies that culminates with an official entry into the cathedral on 7 December and the first Catholic mass the next day . After being shown highlights of the buildings 700m 582m renovation including the massive roof timbers that replace the medieval frame consumed in the fire he will give a speech of thanks to around 1,300 craftsmen and women gathered in the nave . NotreDames revamped interior has been kept a closelyguarded secret with only a few images released over the years marking the progress of the renovation work . But people who have been inside recently say the experience is aweinspiring , the cathedral lifted by a new clarity and brightness that mark a sharp contrast with the pervading gloom of before . Getty Images On 15 April 2019 a major fire engulfed the medieval cathedral of NotreDame in Paris The word that will best capture the day is splendour , said an insider of the Elysée closely involved with the restoration . People will discover the splendour of the cut stone , which is of an immaculate whiteness such as has not been seen in the cathedral maybe for centuries . On the evening of 15 April 2019 , viewers around the world watched aghast as live pictures were broadcast of orange flames spreading along the roof of the cathedral , and then at the peak of the conflagration of the 19th Century spire crashing to the ground . The cathedral whose structure was already a cause for concern before the inferno was undergoing external renovation at the time . Among the theories for the cause of the fire are a cigarette left by a workman , or an electrical fault . Some 600 firefighters battled the flames for 15 hours . At one point , it was feared that the eight bells in the north tower were at risk of falling , which would have brought the tower itself down , and possibly much of the cathedral walls . In the end the structure was saved . What was destroyed were the spire , the wooden roof beams known as the forest , and the stone vaulting over the centre of the transept and part of the nave . There was also much damage from falling wood and masonry , and from water from firehoses . Thankfully what was saved made a much longer list including all the stainedglass windows , most of the statuary and artwork , and the holy relic known as the Crown of Thorns . The organ the second biggest in France was badly affected by dust and smoke , but reparable . In pictures NotreDame interior damage NotreDame A history of Pariss beloved cathedral NotreDame The story of the fire in graphics Cathedral clergy also celebrated certain miraculés miraculous survivors . These include the 14th Century statue in the choir known as the Virgin of the Pillar , which narrowly avoided being crushed by falling masonry . Sixteen massive copper statues of the Apostles and Evangelists , which surrounded the spire , were brought down for renovation just four days before the fire . After inspecting the devastation the next day , Macron made what to many at the time seemed a rash promise to have NotreDame reopened for visitors within five years . A public body to manage the work was created by law , and an appeal for funds brought an immediate response . In all 846m were raised , much from big sponsors but also from hundreds of thousands of small donors . Responsibility for the task was given to JeanLouis Georgelin , a nononsense army general who shared Macrons impatience with committees and the heritage establishment . Theyre used to dealing with frigates . This is an aircraftcarrier , he said . Georgelin is given universal credit for the projects undoubted success , but he died in an accident in the Pyrenees in August 2023 and was replaced by Philippe Jost . An estimated 2,000 masons , carpenters , restorers , roofers , foundryworkers , art experts , sculptors and engineers worked on the project providing a huge boost for French arts and crafts . Many trades such as stonecarving have seen a big increase in apprenticeships as a result of the publicity . The Notre Dame project has been the equivalent of a World Fair , in the way it has been a showcase for our craftsmanship . It is a superb shopwindow internationally , said Pascal PayenAppenzeller , whose association promotes traditional building skills . The first task of the project was to make the site safe , and then to dismantle the massive tangle of metal scaffolding that had previously surrounded the spire but melted in the fire and fused with the stonework . Getty Images Renovation efforts have been ongoing to restore the 850yearold Gothic building since 2019 Early on a decision had to be made about the nature of renovation whether to faithfully recreate the medieval building and the 19th Century neoGothic changes wrought by architect Eugène ViolletleDuc , or to use the opportunity to mark the building with a modern imprint . An appeal for new designs produced unusual ideas , including a glass roof , a green ecoroof , a massive flame instead of a spire , and a spire topped by a vertical laser shooting into the firmament . In the face of opposition from experts and the public , all were abandoned and the reconstruction is essentially true to the original though with some concessions to modern materials and safety requirements . The roof timbers , for example , are now protected with sprinklers and partitioning . The only remaining point of contention is over Macrons desire for a modern design for stainedglass windows in six sidechapels . Artists have submitted entries for a competition , but there is stiff opposition from many in the French arts world . Macron has tried to make the renovation of NotreDame a theme and a symbol . He has closely involved himself with the project , and visited the cathedral several times . At a moment when his political fortunes are at an alltime low following bruising parliamentary elections in July the reopening is a muchneeded boost for morale . Some said he was stealing the limelight by organising Fridays ceremony officially to mark the end of the project a week ahead of the formal reopening . It means that the first , longawaited images of the interior will also inevitably focus on him . In answer Elysée officials point out that the cathedral like all French religious buildings under a law of 1905 belongs to the state , with the Catholic Church its assigned user and that without Macrons rapid mobilisation , the work would never have been completed so quickly . Five years ago everyone thought the presidents promise would be hard to keep , said the Elysée insider . Today we have the proof not only that it was possible but that it was at heart what everyone ardently wanted . What people will see in the new Notre Dame is the splendour and the strength of collective willpower à la française . The grief that comes from lost buildings What NotreDame means to the French Europe France NotreDame Paris
    """
    comparative_analysis(text)