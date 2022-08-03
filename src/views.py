import aiohttp_jinja2
import aiohttp.web
import asyncio
import os
from datetime import datetime, timedelta
from src.db import Site, Data, Logging, Categories
from siteparser import site_data
from sqlalchemy import distinct
import zipfile


@aiohttp_jinja2.template('index.html')
def index(request):
    site = request.app['db_session'].query(Site).all()
    categories = request.app['db_session'].query(distinct(Categories.categories_name)).all()
    unique_category = [c[0] for c in categories]
    return {'site': site, 'categories': unique_category}


@aiohttp_jinja2.template('data.html')
def data_table(request):
    site = request.rel_url.query.getall('site')
    categories = request.rel_url.query.getall('categories')
    site.sort()
    categories.sort()
    file_name = '_'.join([*site, *categories])

    zip_name = f'static/data/{file_name}.zip'

    site_data_one = request.app['db_session'].query(Data).join(Site).filter(Data.categories_name.in_(categories),
                                                                            Site.name == site[0]).order_by(
        Data.product_price.desc())

    if 'empty' not in site:

        site_data_two = request.app['db_session'].query(Data).join(Site).filter(Data.categories_name.in_(categories),
                                                                                Site.name == site[1]).order_by(
            Data.product_price.desc())

        with zipfile.ZipFile(zip_name, 'w') as new_zip:
            for cat in categories:
                new_zip.write(f'static/data/{site[0]}_{cat}.csv', f'goods_data/{site[0]}_{cat}.csv')
                new_zip.write(f'static/data/{site[1]}_{cat}.csv', f'goods_data/{site[1]}_{cat}.csv')

        return {'site_data_one': [site_data_one, site[0]], 'site_data_two': [site_data_two, site[1]], 'file_name': file_name}

    with zipfile.ZipFile(zip_name, 'w') as new_zip:
        for cat in categories:
            new_zip.write(f'static/data/{site[0]}_{cat}.csv', f'goods_data/{site[0]}_{cat}.csv')

    return {"site_data_one": site_data_one, 'site_data_two': None, 'file_name': file_name}


async def parse_data(request):
    data = await request.post()
    try:
        site_list = list(set(data.getall('site')))
        categories_list = data.getall('categories')
        if len(site_list) * ['empty'] == site_list:
            raise KeyError
    except KeyError:
        return aiohttp.web.HTTPFound(
            location=request.app.router['index'].url_for())

    for s in site_list:
        if s == 'empty':
            continue

        site = request.app['db_session'].query(Site).filter(Site.name == s).first()

        for category in categories_list:
            cache = request.app['db_session'].query(Logging).filter(
                Logging.site_id == site.id,
                Logging.categories_name == category).first()

            if cache:
                cache_time = request.app['config']['cache_time']['time']
                delta_cache = timedelta(minutes=cache_time)
                otherness_time = datetime.now() - cache.date_parse

                if otherness_time > delta_cache:
                    request.app['db_session'].query(Data).filter(
                        Data.site_id == site.id,
                        Data.categories_name == category).delete()
                    print(f'Old data from {site.name} categories {category} delete')
                else:
                    continue

            c_option = request.app['db_session'].query(Categories).filter(
                Categories.site_id == site.id,
                Categories.categories_name == category).first()

            await site_data.load_site_data(request, site.domen, category, c_option.categories_url)
    url = request.app.router['data'].url_for().with_query({"site": site_list, "categories": categories_list})
    return aiohttp.web.HTTPFound(url)

