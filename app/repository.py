from typing import Protocol

from sqlmodel import Session, select

from app.dto import URLCreate, URLUpdate
from app.models import URL


class URLRepositoryProtocol(Protocol):
    """Протокол для репозитория URL"""

    def get_all(self, offset: int = 0, limit: int | None = None) -> list[URL]:
        """Получить все URL из базы данных с пагинацией"""
        ...

    def get_total_count(self) -> int:
        """Получить общее количество URL в базе данных"""
        ...

    def get_by_id(self, url_id: int) -> URL | None:
        """Получить URL по ID"""
        ...

    def get_by_short_name(self, short_name: str) -> URL | None:
        """Получить URL по короткому имени"""
        ...

    def create(self, url_data: URLCreate) -> URL:
        """Создать новый URL"""
        ...

    def update(self, url_id: int, url_data: URLUpdate) -> URL | None:
        """Обновить существующий URL"""
        ...

    def delete(self, url_id: int) -> bool:
        """Удалить URL"""
        ...


class URLRepository(URLRepositoryProtocol):
    def __init__(self, session: Session):
        self.session = session

    def get_all(self, offset: int = 0, limit: int | None = None) -> list[URL]:
        """Получить все URL из базы данных с пагинацией"""
        statement = select(URL)
        if limit is not None:
            statement = statement.offset(offset).limit(limit)
        else:
            statement = statement.offset(offset)
        result = self.session.exec(statement)
        return result.all()

    def get_total_count(self) -> int:
        """Получить общее количество URL в базе данных"""
        statement = select(URL)
        result = self.session.exec(statement)
        return len(result.all())

    def get_by_id(self, url_id: int) -> URL | None:
        """Получить URL по ID"""
        statement = select(URL).where(URL.id == url_id)
        result = self.session.exec(statement)
        return result.one_or_none()

    def get_by_short_name(self, short_name: str) -> URL | None:
        """Получить URL по короткому имени"""
        statement = select(URL).where(URL.short_name == short_name)
        result = self.session.exec(statement)
        return result.one_or_none()

    def create(self, url_data: URLCreate) -> URL:
        """Создать новый URL"""
        new_url = URL(
            original_url=url_data.original_url, short_name=url_data.short_name
        )
        self.session.add(new_url)
        self.session.commit()
        self.session.refresh(new_url)
        return new_url

    def update(self, url_id: int, url_data: URLUpdate) -> URL | None:
        """Обновить существующий URL"""
        url = self.get_by_id(url_id)
        if url:
            url.original_url = url_data.original_url
            url.short_name = url_data.short_name
            self.session.commit()
            self.session.refresh(url)
        return url

    def delete(self, url_id: int) -> bool:
        """Удалить URL"""
        url = self.get_by_id(url_id)
        if url:
            self.session.delete(url)
            self.session.commit()
            return True
        return False
