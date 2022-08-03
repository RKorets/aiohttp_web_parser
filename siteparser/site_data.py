import asyncio
import aiohttp
from siteparser.site.rozetka import Rozetka
from siteparser.site.citrus import Citrus
from fake_headers import Headers

SITE = {
    'rozetka.com.ua': Rozetka,
    'ctrs.com.ua': Citrus
}


async def load_site_data(request, site: str, categories_name: str, categories_option_url: str):
    site_option = SITE.get(site)()
    dict_category_list = site_option.get_pages_in_categories(site, categories_option_url)

    header = Headers(browser="chrome", os="win", headers=True).generate()
    async with aiohttp.ClientSession(headers=header) as session:
        tasks = []
        for category_name, url_category_list in dict_category_list.items():
            for url in url_category_list:
                task = asyncio.create_task(site_option.get_page_data(request, session, categories_name, url))
                tasks.append(task)
        await asyncio.gather(*tasks)
