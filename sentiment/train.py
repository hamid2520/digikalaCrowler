from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
import re
import numpy as np
from sklearn.model_selection import train_test_split
from hazm import word_tokenize, Normalizer
import json
import random
import pickle
import tensorflow as tf

from config import *
from model import build_model
from embeding import tokenizer

parser = argparse.ArgumentParser()
parser.add_argument('--full_data_path', '-d', help='Full path of data', default=DATA_PATH)
parser.add_argument('--model_path', '-P', help='Full path of model', default=MODEL_PATH)
parser.add_argument('--processed_pickle_data_path', '-p', help='Full path of processed pickle data',
                    default=PROCESSED_PICKLE_DATA_PATH)
parser.add_argument('--max_length', '-m', help='Maximum length of comments', type=int, default=COMMENT_MAX_LENGTH)
parser.add_argument('--batch_size', '-b', help='Batch size', type=int, default=BATCH_SIZE)
parser.add_argument('--seed', '-s', help='Random seed', type=int, default=SEED)
parser.add_argument('--epoch', '-e', help='Epochs', type=int, default=EPOCH)
parser.add_argument('--training_data_ready', '-t', help='Pass when trainning data is ready', action='store_true')
parser.add_argument('--data_model_ready', '-M', help='Pass when data model is ready', action='store_true')
normalizer = Normalizer()


def filter_data(full_path):
    with open(full_path, 'r', encoding='utf8') as f:
        products = []
        for row in f.readlines():
            raw_data = json.loads(row)
            comments = raw_data.get('cmts', None)
            rate = raw_data.get('r', None)
            cat = raw_data.get('c', None)
            if comments is None or len(comments) == 0 or cat is None or rate is None:
                continue
            valid_comments = []
            for comment in comments:
                pol = comment.get('pol', None)
                if pol is not None and pol != 0:
                    valid_comments.append(comment)
            if len(valid_comments) == 0:
                continue
            raw_data['cmts'] = valid_comments
            products.append(raw_data)
        return products


def tokenize_text(text):
    text = text.replace('.', ' ')
    text = re.sub('\s+', ' ', text).strip()
    text = text.replace('\u200c', ' ').replace('\n', '').replace('\r', '').replace('ي', 'ی').replace('ك', 'ک')
    normalized_text = normalizer.normalize(text)
    tokens = word_tokenize(normalized_text)
    return tokens


def process_data(products):
    categories_set = set()
    all_comments = []
    for product in products:
        product_category = product.get('c', None)
        categories_set.add(product_category)
        comments = product.get('cmts', [])
        for comment_dict in comments:
            pol = comment_dict.get('pol', None)
            if pol is None:
                print('err')
            if pol == -1:
                pol = 0
            text = comment_dict.get('txt', '')
            if text is None:
                text = ''
            tokens = tokenize_text(text)
            all_comments.append({
                'pol': pol,
                'tokens': tokens
            })
    return all_comments


def prepare_training_data(processed_comments, word_idx):
    X = []
    y = []
    for comment in processed_comments:
        X.append([word_idx[token] for token in comment['tokens']])
        y.append(comment['pol'])
    return np.asarray(X), np.asarray(y)


def create_word_set(comments):
    word_set = set()
    for comment in comments:
        for token in comment['tokens']:
            word_set.add(token)
    return word_set


def create_word_index(words_iterable):
    result = dict()
    i = 1
    for w in words_iterable:
        result[w] = i
        i += 1
    result['UNK'] = i
    return result


def main(argv):
    args = parser.parse_args(argv[1:])
    print(args.batch_size, args.epoch)
    data_path = args.full_data_path

    batch_size = args.batch_size
    random.seed(args.seed)

    is_training_data_ready = args.training_data_ready
    is_data_model_ready = args.data_model_ready
    pickle_data_path = args.processed_pickle_data_path
    model_path = args.model_path
    epoch = args.epoch
    max_length_of_comment = args.max_length

    if is_training_data_ready:
        with open(pickle_data_path, 'rb') as f:  # default: processed_data.pickle
            X, y, word_idx = pickle.load(f)
    else:
        print('Filtering data...')
        products = filter_data(data_path)  # default: data/results.jl

        print('Processing data...')
        all_comments = process_data(products)

        print('Create word set...')
        word_set = create_word_set(all_comments)

        print('Create word to index...')
        word_idx = create_word_index(word_set)

        print('Prepare training data...')
        X, y = prepare_training_data(all_comments, word_idx)

        with open(PROCESSED_PICKLE_DATA_PATH, 'wb') as f:
            pickle.dump((X, y, word_idx), f)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    X_train = tf.keras.preprocessing.sequence.pad_sequences(X_train, maxlen=max_length_of_comment)
    X_test = tf.keras.preprocessing.sequence.pad_sequences(X_test, maxlen=max_length_of_comment)

    if is_data_model_ready:
        model = tf.keras.models.load_model(model_path)
    else:
        model = build_model(len(word_idx))
        model.fit(X_train, y_train,
                  batch_size=batch_size,
                  epochs=epoch,
                  validation_data=(X_test, y_test))
        model.save(MODEL_PATH)

    y_pred = model.predict(X_test, batch_size=batch_size)

    acc_sum = 0

    real_count = [0, 0]
    pred_count = [0, 0]
    true_count = [0, 0]

    for i in range(y_pred.shape[0]):
        label = y_test[i]
        pred = y_pred[i]
        plabel = -1

        if pred[label] > pred[1 - label]:
            plabel = label
        else:
            plabel = 1 - label

        real_count[label] += 1
        pred_count[plabel] += 1

        if label == plabel:
            acc_sum += 1
            true_count[label] += 1

    print('acc', acc_sum / y_pred.shape[0])
    print(real_count)
    print(pred_count)
    print(true_count)

    p_negative = true_count[0] / pred_count[0]
    p_positive = true_count[1] / pred_count[1]

    r_negative = true_count[0] / real_count[0]
    r_positive = true_count[1] / real_count[1]

    print("p-", p_negative)
    print("p+", p_positive)
    print("r-", r_negative)
    print("r+", r_positive)

    f1_negative = 2 * (p_negative * r_negative) / (p_negative + r_negative)
    f1_positive = 2 * (p_positive * r_positive) / (p_positive + r_positive)

    print("f1-", f1_negative)
    print("f1+", f1_positive)


if __name__ == '__main__':
    tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.INFO)
    tf.compat.v1.app.run(main)
