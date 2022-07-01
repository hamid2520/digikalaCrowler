import requests
import pandas as pd

url = 'https://api.torob.com/v4/base-product/search'
params = {'sort': 'popularity', 'category': 94, 'page': 0, 'size': 5000}
image_urls = []
info_urls = []
persian_names = []
english_names = []
prices = []
specs = []
brands = []
sims = []
capacities = []

try:
    while True:
        resp = requests.get(url, params=params).json()
        count = resp['count']
        print(params['page'], len(resp['results']), len(prices))
        for mobile in resp['results']:
            image_urls.append(mobile['image_url'])
            info_urls.append(mobile['more_info_url'])
            persian_names.append(mobile['name1'])
            english_names.append(mobile['name2'])
            prices.append(mobile['price_text'].split()[0])
            more_info_url = mobile['more_info_url']
            more_resp = requests.get(more_info_url).json()
            brands.append(more_resp['attributes'].get('brand', None))
            sims.append(more_resp['attributes'].get('sims', '1'))
            capacities.append(more_resp['attributes'].get('capacity', None))
            if len(more_resp['structural_specs']['headers']) > 0:
                specs.append(more_resp['structural_specs']['headers'][0]['specs'])
        params['page'] += 1
        if count <= len(prices) or len(resp['results']) == 0:
            break
except Exception as e:
    print(e)

mobile_dict = {'Image url': image_urls, 'Info url': info_urls, 'Persian name': persian_names,
               'English name': english_names, 'price': prices, 'spec': specs, 'brand': brands, 'sim': sims,
               'capacity': capacities}
df = pd.DataFrame(mobile_dict)
df.to_csv('../data/torob_mobiles.csv', encoding='utf-8')
