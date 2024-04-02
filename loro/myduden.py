import duden
import spacy
nlp = spacy.load("de_core_news_lg")


rechtschreibung = {
    'Ä' : 'Ae',
    'Ö' : 'Oe',
    'Ü' : 'Ue',
    'ä' : 'ae',
    'ö' : 'oe',
    'ü' : 'ue',
    'ß' : 'sz'
}

def get_rechtschreibung(word):
    recht_word = ''
    for letter in word:
        if letter in rechtschreibung:
            recht_word += rechtschreibung[letter]
        else:
            recht_word += letter
    return recht_word

words = ['Öffentlichkeit', 'Übung', 'Ärger', 'Österreich', 'Überlegenheit', 'Änderung', 'Übersee', 'Ökonomie', 'Überzeugung', 'Möbel', 'Überprüfen', 'Lärm', 'Türkei', 'Fußball', 'Größe', 'vögeln', 'Hälfte', 'Brötchen', 'Mütze']
doc = nlp(' '.join(words))
for token in doc:
    thisword = token.lemma_
    if token.pos_ == 'VERB':
        recht_word = get_rechtschreibung(thisword.lower())
    else:
        recht_word = get_rechtschreibung(thisword)
    w = duden.get(recht_word)
    if w is None:
        print("Word '%s' ('%s') not found in Duden" % (thisword, recht_word))

    else:
        try:
            if token.pos_ == 'VERB':
                assert thisword.lower() == w.name
            else:
                assert thisword == w.name
            print("Rechtschreibung word for '%s' is '%s'" % (thisword, recht_word))
        except AssertionError:
            print("Error: %s != %s", thisword, w.name)


