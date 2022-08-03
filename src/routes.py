from aiohttp.web import Application
from src.views import index, parse_data, data_table


def setup_routes(app: Application):
    app.router.add_get('/', index, name='index')
    app.router.add_route('POST', '/', parse_data)
    app.router.add_get('/data', data_table, name='data')

    app.router.add_static('/css/',
                          path='static/css',
                          name='css')
    app.router.add_static('/fonts/',
                          path='static/fonts',
                          name='fonts')
    app.router.add_static('/images/',
                          path='static/images',
                          name='images')
    app.router.add_static('/js/',
                          path='static/js',
                          name='js')

    app.router.add_static('/data/',
                          path='static/data',
                          name='data_parse')
