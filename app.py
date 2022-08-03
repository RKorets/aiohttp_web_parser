import asyncio
import sys
import aiohttp_jinja2
import jinja2
from aiohttp import web
from src.routes import setup_routes
from src.settings import config, BASE_DIR
from src.db import pg_context

app = web.Application()
app['config'] = config
app['static_root_url'] = '/static'
aiohttp_jinja2.setup(app,
                     loader=jinja2.FileSystemLoader(str(BASE_DIR / 'src' / 'templates')))
setup_routes(app)
app.cleanup_ctx.append(pg_context)
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
web.run_app(app)
