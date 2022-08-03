import re
import csv
from datetime import datetime
from bs4 import BeautifulSoup
from collections import defaultdict
from siteparser.site.site_interface import Interface
from src.db import Logging, Data, Site


class Citrus(Interface):

    @staticmethod
    def get_pages_in_categories(site: str, categories: str) -> dict:
        promo_category_element = defaultdict(list)

        for page in range(1, 4):
            promo_category_element[categories].append(f'https://{site}/' + categories + f'page_{page}/')
        return promo_category_element

    @staticmethod
    async def get_page_data(request, session, category: str, link) -> str:
        site = request.app['db_session'].query(Site).filter(Site.name == 'Citrus').first()
        with open(f'static/data/Citrus_{category}.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerow((
                'Goods',
                'Price',
                'URL'
            ))

        async with session.get(link) as resp:
            print(f'get url: {link}')
            resp_text = await resp.text()
            soup = BeautifulSoup(resp_text, 'lxml')

            cards = soup.find_all('div', class_=re.compile("br10 p8 border-box pr productCardCategory-0-2"))

            for item in cards:
                try:
                    price = item.find('div', class_=re.compile('medium fz16 price-0-2')) \
                                .text.replace(' ', '').strip()[:-1]
                    goods_name = item.find('a', class_=re.compile('link line-clamp-2 break-word link-0-2')) \
                        .text.strip()
                    goods_url_sufix = item.find('a', class_=re.compile('link line-clamp-2 break-word link-0-2')) \
                        .get('href')
                    goods_url = 'https://www.ctrs.com.ua/' + goods_url_sufix
                except AttributeError:
                    print('citrus AttributeError')
                    continue

                with open(f'static/data/Citrus_{category}.csv', 'a') as file:
                    writer = csv.writer(file)
                    writer.writerow((
                        goods_name,
                        price,
                        goods_url,
                    ))

                data = Data(product_name=goods_name, product_price=int(price), product_url=goods_url,
                            categories_name=category, site_id=site.id)
                request.app['db_session'].add(data)
            cache = request.app['db_session'].query(Logging).filter(
                Logging.site_id == site.id,
                Logging.categories_name == category).first()
            if cache:
                request.app['db_session'].query(Logging).filter(
                    Logging.site_id == site.id,
                    Logging.categories_name == category).update({Logging.date_parse: datetime.now()})
            else:
                cache = Logging(site_id=site.id, categories_name=category, date_parse=datetime.now())
                request.app['db_session'].add(cache)
            request.app['db_session'].commit()

        return resp_text
