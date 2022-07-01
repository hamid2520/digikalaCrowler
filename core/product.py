from flask import request
import json
import os
from pathlib import Path

path = Path(__file__).parent.absolute()


def get_product():
    if 'product_id' in request.args:
        with open(os.path.join(path, '../data/digikala_mobiles.jl'), 'r', encoding='utf8') as f:
            for row in f.readlines():
                data = json.loads(row)
                if data['id'] != request.args['product_id']:
                    continue
                spec = data.get('spec', None)
                data['date'] = spec['مشخصات کلی'].get('زمان معرفی', None)
                data['sim'] = spec['مشخصات کلی'].get('تعداد سیم کارت', 'یک سیم کارت')
                data['memory'] = spec.get('حافظه', {}).get('حافظه داخلی', None)
                return json.dumps({
                    'success': True,
                    'product': data
                })
        return json.dumps({
            'success': False,
            'error': 'product not found'
        })
    return json.dumps({
        'success': False,
        'error': 'parameter missing'
    })
