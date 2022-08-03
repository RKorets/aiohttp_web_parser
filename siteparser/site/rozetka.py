import csv
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from collections import defaultdict
from fake_headers import Headers
from siteparser.site.site_interface import Interface
from src.db import Logging, Data, Site


class Rozetka(Interface):

    @staticmethod
    def get_pages_in_categories(site: str, categories: str) -> dict:
        promo_category_element = defaultdict(list)
        header = Headers(
            browser="chrome",
            os="win",
            headers=True
        ).generate()

        response = requests.get(url=f'https://{site}/' + categories, headers=header)

        soup = BeautifulSoup(response.text, 'lxml')
        pagination_link = soup.find_all('a', class_='pagination__link ng-star-inserted')

        promo_category_element[categories].append(f'https://{site}/' + categories)

        for page in pagination_link:
            page_url = page.get('href')[1:]
            promo_category_element[categories].append(f'https://{site}/' + page_url)

        return promo_category_element

    @staticmethod
    async def get_page_data(request, session, category: str, link) -> str:
        site = request.app['db_session'].query(Site).filter(Site.name == 'Rozetka').first()
        with open(f'static/data/Rozetka_{category}.csv', 'w') as file:
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

            cards = soup.find_all('div', class_='goods-tile ng-star-inserted')

            for item in cards:
                try:

                    price = item.find('span', class_='goods-tile__price-value').text.replace(' ', '').strip()
                    goods_url = item.find('a', class_='goods-tile__heading ng-star-inserted').get('href')
                    goods_name = item.find('span', class_='goods-tile__title').text.strip()

                except AttributeError:
                    print('rozetka AttributeError')
                    continue

                with open(f'static/data/Rozetka_{category}.csv', 'a') as file:
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

# rozetka = Site()
