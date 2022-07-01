from hazm import word_tokenize, Normalizer
import re

normalizer = Normalizer()


class Tokenizer(object):
    def __init__(self):
        pass

    def tokenize(self, text):
        text = self.remove_symbols(text)
        text = re.sub('\s+', ' ', text).strip()
        text = text.lower()
        text = text.replace('\u200c', ' ').replace('\n', '').replace('\r', '').replace('ي', 'ی').replace('ك', 'ک')
        # text = re.sub(r"([0-9]+(\.[0-9]+)?)",r" \1 ", text).strip()
        # normalized_text = normalizer.normalize(text)
        return word_tokenize(text)

    def remove_symbols(self, text):
        text = text.replace('-', ' ').replace('/', ' ').replace('(', '').replace(')', '')
        return text
