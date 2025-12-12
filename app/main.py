from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import router
from app.database import create_db_and_tables


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ping")
async def get_pong():
    return "pong"


app.include_router(router, prefix="/api")
