import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api import router
from app.database import create_db_and_tables
from app.dependencies import get_url_repository
from app.repository import URLRepositoryProtocol


@asynccontextmanager
async def lifespan(_: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

# Получаем разрешенные origins из переменных окружения
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["Content-Range"],
)


@app.get("/ping")
async def get_pong():
    return "pong"


@app.get("/r/{short_name}", name="redirect_link")
async def redirect_link(
    short_name: str,
    repository: URLRepositoryProtocol = Depends(get_url_repository),
) -> RedirectResponse:
    """Редирект по короткому имени ссылки"""
    url = await repository.get_by_short_name(short_name)
    if url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link with short name '{short_name}' not found",
        )
    return RedirectResponse(url.original_url)


app.include_router(router, prefix="/api")
