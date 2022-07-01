from __future__ import absolute_import, division, print_function, unicode_literals
import pickle
import tensorflow as tf
from sentiment.config import *
from hazm import word_tokenize, Normalizer
import re
import os
from pathlib import Path

path = Path(__file__).parent.absolute()
normalizer = Normalizer()


def tokenize_text(text):
    text = text.replace('.', ' ')
    text = re.sub('\s+', ' ', text).strip()
    text = text.replace('\u200c', ' ').replace('\n', '').replace('\r', '').replace('ي', 'ی').replace('ك', 'ک')
    normalized_text = normalizer.normalize(text)
    tokens = word_tokenize(normalized_text)
    return tokens


with open(os.path.join(path, PROCESSED_PICKLE_DATA_PATH), 'rb') as f:  # default: processed_data.pickle
    X, y, word_idx = pickle.load(f)

model = tf.keras.models.load_model(os.path.join(path, MODEL_PATH))


def predict(text):
    tokens = tokenize_text(text)
    tokens_idx = [[word_idx.get(token, word_idx['UNK']) for token in tokens]]
    X_interactive = tf.keras.preprocessing.sequence.pad_sequences(tokens_idx, maxlen=COMMENT_MAX_LENGTH)
    result = model.predict(X_interactive)
    return round(result[0][1] * 100, 4)
    # print(' - : ', str(round(result[0][0] * 100, 4)) + '%')
    # print(' + : ', str(round(result[0][1] * 100, 4)) + '%', '\n')
