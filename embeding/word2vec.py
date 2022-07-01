import pandas as pd
import numpy as np
import gensim
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.pipeline import Pipeline

from embeding import tokenizer
from scipy import spatial

from embeding.tfidf_embeding import TfidfEmbeddingVectorizer

df = pd.read_csv('../data/digikala_mobiles.csv')
df = df[df['title_fa'].notna()]
df = df[df['title_en'].notna()]
tokenizer = tokenizer.Tokenizer()


def avg_feature_vector(sentence, model, num_features, index2word_set):
    words = tokenizer.tokenize(sentence)
    feature_vec = np.zeros((num_features,), dtype='float32')
    n_words = 0
    for word in words:
        if word in index2word_set:
            n_words += 1
            feature_vec = np.add(feature_vec, model[word])
    if n_words > 0:
        feature_vec = np.divide(feature_vec, n_words)
    return feature_vec


def train(dataset):
    tokens = [tokenizer.tokenize(t) for t in dataset]
    model = gensim.models.Word2Vec(sentences=tokens, size=300, window=5, min_count=1, workers=4, sg=1)
    model.wv.save_word2vec_format('../models/word2vec_cbow.txt', binary=False)
    return model


def load_model():
    model = gensim.models.KeyedVectors.load_word2vec_format('../models/word2vec_cbow.txt')
    return model


dataset = []
for text in df['title_fa']:
    dataset.append(text)
for text in df['title_en']:
    dataset.append(text)
# for item in dataset:
#     print('--------')
#     print(item)
#     print(tokenizer.tokenize(item))

# w2v_model = train(dataset)

# for word in w2v_model.wv.vocab:
#     print(word)

w2v_model = load_model()
index2word_set = set(w2v_model.index2word)

# w2v_tfidf = Pipeline([
#     ("word2vec vectorizer", TfidfEmbeddingVectorizer(w2v_model)),
#     ("extra trees", ExtraTreesClassifier(n_estimators=200))])

query = dataset[0]
print(query)
qafv = avg_feature_vector(query, model=w2v_model, num_features=300, index2word_set=index2word_set)
results = []
i = 0
for item in dataset[1:]:
    # afv = avg_feature_vector(item, model=w2v_model, num_features=300, index2word_set=index2word_set)
    # if list(afv) == [0] * len(afv):
    #     sim = 0
    # else:
    #     sim = 1 - spatial.distance.cosine(afv, qafv)
    # results.append((i, sim))
    results.append((i, w2v_model.n_similarity(tokenizer.tokenize(query), tokenizer.tokenize(item))))
    i += 1
results = sorted(results, key=lambda xy: xy[1], reverse=True)
for x in results[:10]:
    print(dataset[x[0]])