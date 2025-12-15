from pydantic import BaseModel

from app.config import BASE_URL
from app.models import URL


class URLCreate(BaseModel):
    original_url: str
    short_name: str


class URLUpdate(BaseModel):
    original_url: str
    short_name: str


class URLResponse(BaseModel):
    id: int
    original_url: str
    short_name: str
    short_url: str

    @classmethod
    def from_url(cls, url: "URL") -> "URLResponse":
        """Создать URLResponse из модели URL"""
        return cls(
            id=url.id,
            original_url=url.original_url,
            short_name=url.short_name,
            short_url=f"{BASE_URL}/r/{url.short_name}",
        )


class PaginationParams(BaseModel):
    """Параметры пагинации"""

    offset: int = 0
    limit: int = 10

    @classmethod
    def from_range(cls, range_str: str) -> "PaginationParams":
        """Парсит строку range в формате [start,end]"""
        try:
            # Убираем квадратные скобки и разделяем по запятой
            range_str = range_str.strip("[]")
            start, end = map(int, range_str.split(","))
            return cls(offset=start, limit=end - start)
        except (ValueError, AttributeError):
            return cls()
