from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.dto import URLCreate, URLUpdate
from app.models import URL


class URLRepositoryProtocol(Protocol):
    """Протокол для репозитория URL"""

    async def get_all(self) -> list[URL]:
        """Получить все URL из базы данных"""
        ...

    async def get_by_id(self, url_id: int) -> URL | None:
        """Получить URL по ID"""
        ...

    async def get_by_short_name(self, short_name: str) -> URL | None:
        """Получить URL по короткому имени"""
        ...

    async def create(self, url_data: URLCreate) -> URL:
        """Создать новый URL"""
        ...

    async def update(self, url_id: int, url_data: URLUpdate) -> URL | None:
        """Обновить существующий URL"""
        ...

    async def delete(self, url_id: int) -> bool:
        """Удалить URL по ID"""
        ...


class URLRepository(URLRepositoryProtocol):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[URL]:
        """Получить все URL из базы данных"""
        statement = select(URL)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_id(self, url_id: int) -> URL | None:
        """Получить URL по ID"""
        statement = select(URL).where(URL.id == url_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_short_name(self, short_name: str) -> URL | None:
        """Получить URL по короткому имени"""
        statement = select(URL).where(URL.short_name == short_name)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def create(self, url_data: URLCreate) -> URL:
        """Создать новый URL"""
        new_url = URL(
            original_url=url_data.original_url, short_name=url_data.short_name
        )
        self.session.add(new_url)
        await self.session.commit()
        await self.session.refresh(new_url)
        return new_url

    async def update(self, url_id: int, url_data: URLUpdate) -> URL | None:
        """Обновить существующий URL"""
        url = await self.get_by_id(url_id)
        if url:
            url.original_url = url_data.original_url
            url.short_name = url_data.short_name
            await self.session.commit()
            await self.session.refresh(url)
        return url

    async def delete(self, url_id: int) -> bool:
        """Удалить URL по ID"""
        url = await self.get_by_id(url_id)
        if url:
            await self.session.delete(url)
            await self.session.commit()
            return True
        return False
