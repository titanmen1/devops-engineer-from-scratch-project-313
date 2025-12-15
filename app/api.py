from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from app.dependencies import get_url_repository
from app.dto import PaginationParams, URLCreate, URLResponse, URLUpdate
from app.repository import URLRepositoryProtocol

router = APIRouter()


@router.get("/links", response_model=List[URLResponse])
async def get_links(
    response: Response,
    range: str = Query(None, description="Pagination range in format [start,end]"),
    repository: URLRepositoryProtocol = Depends(get_url_repository),
) -> List[URLResponse]:
    """Получает список ссылок с поддержкой пагинации"""
    # Парсим параметры пагинации
    pagination = PaginationParams.from_range(range) if range else PaginationParams()

    # Получаем данные с пагинацией
    urls = await repository.get_all(offset=pagination.offset, limit=pagination.limit)
    total_count = await repository.get_total_count()

    # Формируем заголовок Content-Range
    start = pagination.offset
    # Если есть записи, end = start + количество возвращенных записей - 1
    # Если записей нет, используем start - 1 (или можно оставить start)
    if urls:
        end = start + len(urls) - 1
    else:
        # Если записей нет, можно использовать формат "links */total"
        # или "links 0--1/0" для пустого результата
        end = start - 1 if total_count == 0 else start

    response.headers["Content-Range"] = f"links {start}-{end}/{total_count}"

    return [URLResponse.from_url(url) for url in urls]


@router.get("/links/{link_id}", response_model=URLResponse)
async def get_link(
    link_id: int, repository: URLRepositoryProtocol = Depends(get_url_repository)
) -> URLResponse:
    """Получает данные ссылки по идентификатору"""
    url = await repository.get_by_id(link_id)
    if not url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link with id {link_id} not found",
        )

    return URLResponse.from_url(url)


@router.post("/links", response_model=URLResponse, status_code=status.HTTP_201_CREATED)
async def create_link(
    url_data: URLCreate, repository: URLRepositoryProtocol = Depends(get_url_repository)
) -> URLResponse:
    """Создает новую короткую ссылку"""
    if not url_data.short_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Field 'short_name' is required",
        )

    existing_url = await repository.get_by_short_name(url_data.short_name)
    if existing_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Short name '{url_data.short_name}' already exists",
        )

    created_url = await repository.create(url_data)
    return URLResponse.from_url(created_url)


@router.put("/links/{link_id}", response_model=URLResponse)
async def update_link(
    link_id: int,
    url_data: URLUpdate,
    repository: URLRepositoryProtocol = Depends(get_url_repository),
) -> URLResponse:
    """Обновляет существующую ссылку"""
    # Проверяем существование ссылки
    existing_url = await repository.get_by_id(link_id)
    if not existing_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link with id {link_id} not found",
        )

    # Проверяем, не занято ли новое короткое имя другой ссылкой
    url_with_same_short_name = await repository.get_by_short_name(url_data.short_name)
    if url_with_same_short_name and url_with_same_short_name.id != link_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Short name '{url_data.short_name}' already exists",
        )

    updated_url = await repository.update(link_id, url_data)
    return URLResponse.from_url(updated_url)


@router.delete("/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    link_id: int, repository: URLRepositoryProtocol = Depends(get_url_repository)
) -> None:
    """Удаляет ссылку"""
    deleted = await repository.delete(link_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link with id {link_id} not found",
        )
