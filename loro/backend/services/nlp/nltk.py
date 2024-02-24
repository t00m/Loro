import nltk
# https://data-dive.com/german-nlp-binary-text-classification-of-reviews-part1/
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# ~ corp = nltk.corpus.ConllCorpusReader('.', 'tiger_release_aug07.corrected.16012013.conll09', ['ignore', 'words', 'ignore', 'ignore', 'pos'], encoding='utf-8')

nltk.download('punkt')
nltk.download('tagsets')
nltk.download('averaged_perceptron_tagger')
# ~ #nltk.download('german_tagset')
# ~ #nltk.download('stts')
nltk.download('stopwords')

stemmer = SnowballStemmer("german")
stop_words = set(stopwords.words("german"))

def process_sentence(sentence: str) -> None:
    clean_sentence = clean_text(sentence)
    print("Clean sentence: %s" % clean_sentence)
    tokens = tokenize_sentence(clean_sentence)
    tagged_tokens = pos_tagging(tokens)
    print("Tokens: %s" % tokens)
    print("Tagged tokens: %s" % tagged_tokens)
    # ~ for token in tokens:
        # ~ translate_text(text=token)
    # ~ translate_text(text=sentence)

def tokenize_sentence(text: str) -> []:
    text_lowercase = text.lower()
    tokens = nltk.word_tokenize(text_lowercase)
    return tokens

def pos_tagging(tokens: []) -> []:
    return nltk.pos_tag(tokens)

def named_entity_recognition(tokens: []) -> []:
    from nltk.chunk import conll2002_io
    text_tagged = nltk.tag.perceptron.PerceptronTagger().tag(tokens)
    entities = conll2002_io.parse(text_tagged)
    return entities
    # ~ for chunk in entities.tagged_sents:
        # ~ for t in chunk:
            # ~ if t[1] not in ['B-ORG', 'I-ORG', 'B-PER', 'I-PER', 'B-LOC', 'I-LOC']:
                # ~ print(t[0] + "/" + t[1])
