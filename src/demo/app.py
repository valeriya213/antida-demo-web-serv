from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import settings
from .accounts import api as accounts_api

app = FastAPI()
app.mount(settings.static_url, StaticFiles(directory=settings.static_directory), name='static')
accounts_api.initialize_app(app)
