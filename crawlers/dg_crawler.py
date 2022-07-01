import json
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
from flask import request
from sentiment import test

digits = {'یک': 1, 'دو': 2, 'سه': 3}


def create_dataset():
    with open('../data/digikala_mobiles.jl', 'r', encoding='utf8') as f:
        products = []
        for row in f.readlines():
            raw_data = json.loads(row)
            spec = raw_data.get('spec', None)
            del raw_data['spec']
            raw_data['date'] = spec['مشخصات کلی'].get('زمان معرفی', None)
            raw_data['sim'] = spec['مشخصات کلی'].get('تعداد سیم کارت', 'یک سیم کارت')
            # digits[spec['مشخصات کلی'].get('تعداد سیم کارت', 'یک سیم کارت').replace(' سیم کارت', '')]
            raw_data['memory'] = spec.get('حافظه', {}).get('حافظه داخلی', None)
            products.append(raw_data)

        df = pd.DataFrame(products)
        df.to_csv('../data/digikala_mobiles.csv', encoding='utf-8')


def get_comments():
    if 'product_id' in request.args:
        comments = []
        html = urlopen('https://www.digikala.com/ajax/product/comments/{}/?mode=buyers'.format(request.args['product_id']))
        soup = BeautifulSoup(html, 'html.parser')

        for comment_section in soup.find_all('div', {'class': 'article'}):
            text = comment_section.p.get_text()
            comments.append({'text': text, 'pos': test.predict(text)})
        if 'filter' in request.args:
            if request.args['filter'] == 'pos':
                pass
            elif request.args['filter'] == 'neg':
                pass
        return json.dumps({
            'success': True,
            'comments': comments
        })
    return json.dumps({
        'success': False,
        'error': 'parameter missing'
    })