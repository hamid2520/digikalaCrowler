import scrapy
import re
import logging


class ProductSpider(scrapy.Spider):
    name = 'product'
    products_count = 0
    brands = {}
    start_urls = [
        'http://digikala.com/search/category-mobile-phone/',
    ]

    def parse(self, response):
        for href in response.css('div.js-product-box a'):
            yield response.follow(href, self.parse_product)

        # follow pagination links
        for url in response.css('a.c-pager__item::attr(href)').extract():
            tokens = url.split('pageno=')
            if len(tokens) > 1:
                page_num = tokens[1]
                yield response.follow('?pageno={}'.format(page_num), self.parse)

    def parse_product(self, response):
        def extract_with_css(query):
            res = response.css(query).extract_first()
            return res.strip() if res is not None else None
        res = re.search('(.*)dkp-(.*)/(.*)', response.url)
        id = res.group(2)
        brand = extract_with_css('div.c-product__directory a::attr(href)').split('/')[-2]
        if brand not in self.brands:
            self.brands[brand] = 1
        else:
            self.brands[brand] += 1
        self.products_count += 1
        spec = {}
        spec_selector = response.css('.c-params')
        for spec_section in spec_selector.css('section'):
            params_title = spec_section.css('.c-params__title::text').extract_first().strip()
            spec[params_title] = {}
            last_key = ''
            for x in spec_section.css('.c-params__list li'):
                key = ' '.join(x.css('.c-params__list-key span::text').extract()).strip()
                if len(key) == 0:
                    key = ' '.join(x.css('.c-params__list-key a::text').extract()).strip()
                value = re.sub(' +', ' ', ' '.join(x.css('.c-params__list-value span::text')
                                                   .extract()).replace('\n', ' ')).strip()
                if len(key) == 0:
                    if len(value) > 0:
                        # print('-------')
                        # print(last_key)
                        # print(spec[params_title][last_key])
                        spec[params_title][last_key] += '\n' + value.strip()
                        # print(spec[params_title][last_key])
                else:
                    spec[params_title][key] = value
                    last_key = key
        print(self.products_count)
        yield {
            'id': id,
            'title_fa': extract_with_css('.c-product__title::text'),
            'title_en': extract_with_css('.c-product__title-en::text'),
            'price': extract_with_css('.c-price__value::text'),
            'rate': extract_with_css('.c-product__engagement-rating::text'),
            'brand_fa': extract_with_css('div.c-product__directory a::text'),
            'brand_en': brand,
            'spec': spec
        }