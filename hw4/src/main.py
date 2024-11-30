from fastapi import FastAPI
from api import info, get_all, get_new, get_known, get, initdb

app = FastAPI()

app.include_router(info.router)
app.include_router(get_all.router)
app.include_router(get_new.router)
app.include_router(get_known.router)
app.include_router(get.router)
app.include_router(initdb.router)