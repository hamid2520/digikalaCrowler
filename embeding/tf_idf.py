import pandas as pd
import numpy as np
import gensim
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from embeding import tokenizer
from pathlib import Path
from flask import request
import json

path = Path(__file__).parent.absolute()
df = pd.read_csv(os.path.join(path, '../data/digikala_mobiles.csv'))
df = df[df['title_fa'].notna()]
df = df[df['title_en'].notna()]
tokenizer = tokenizer.Tokenizer()

dataset = []
for text in df['title_fa']:
    text = ' '.join(tokenizer.tokenize(text))
    dataset.append(text)
for text in df['title_en']:
    text = ' '.join(tokenizer.tokenize(text))
    dataset.append(text)

vectorizer = TfidfVectorizer(use_idf=True)
tfIdf = vectorizer.fit_transform(dataset)


def search():
    if 'query' in request.args:
        limit = 10
        if 'limit' in request.args:
            limit = int(request.args['limit'])
        offset = 0
        if 'offset' in request.args:
            offset = int(request.args['offset'])
        query = request.args['query']
        query_vec = vectorizer.transform([query])
        products = np.array([x[0] for x in cosine_similarity(tfIdf, query_vec)])
        if offset > 0:
            products = products.argsort()[-offset - limit: -offset][::-1].tolist()
        else:
            products = products.argsort()[-limit:][::-1].tolist()
        results = []
        dic = df.to_dict(orient='records')
        for item in products:
            index = item
            if item > df.shape[0]:
                index = item - df.shape[0]
            results.append(dic[index])
        return json.dumps({
            'success': True,
            'results': results
        })
    return json.dumps({
        'success': False,
        'error': 'parameter missing'
    })
