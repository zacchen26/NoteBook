import spacy
import re

class TextProcessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")

    def process(self, text):
        text = re.sub(r'\W+', ' ', text.lower())
        doc = self.nlp(text)
        return " ".join(token.lemma_ for token in doc if not token.is_stop and not token.is_punct)
