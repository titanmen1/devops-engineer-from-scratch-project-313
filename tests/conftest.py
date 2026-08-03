import os
from collections.abc import AsyncIterator, Callable, Iterator
from itertools import count

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Connection, Engine
from sqlmodel import Session, SQLModel, create_engine

from app.database import get_session
from app.main import app
from app.models import URL

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/urlshortener_test",
)


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    """Движок тестовой базы данных со схемой, создаваемой на время прогона"""
    engine = create_engine(TEST_DATABASE_URL)
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def connection(engine: Engine) -> Iterator[Connection]:
    """Соединение с внешней транзакцией, которая откатывается после теста"""
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            yield connection
        finally:
            transaction.rollback()


@pytest.fixture
def db_session(connection: Connection) -> Iterator[Session]:
    """Сессия внутри внешней транзакции

    Коммиты приложения превращаются в savepoint'ы, поэтому изменения теста
    откатываются вместе с внешней транзакцией и не видны другим тестам.
    """
    with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
        yield session


@pytest.fixture
async def client(db_session: Session) -> AsyncIterator[AsyncClient]:
    """HTTP-клиент приложения, работающего с тестовой сессией"""
    app.dependency_overrides[get_session] = lambda: db_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def create_link(db_session: Session) -> Callable[..., URL]:
    """Фабрика ссылок: сохраняет ссылку в базе и возвращает её"""
    counter = count(1)

    def factory(original_url: str | None = None, short_name: str | None = None) -> URL:
        number = next(counter)
        link = URL(
            original_url=original_url or f"https://example{number}.com",
            short_name=short_name or f"example{number}",
        )
        db_session.add(link)
        db_session.commit()
        db_session.refresh(link)
        return link

    return factory


@pytest.fixture
def link(create_link: Callable[..., URL]) -> URL:
    """Одна сохранённая ссылка"""
    return create_link(original_url="https://example.com", short_name="example")


@pytest.fixture
def links(create_link: Callable[..., URL]) -> list[URL]:
    """Набор ссылок, помещающийся на страницу по умолчанию"""
    return [create_link() for _ in range(3)]


@pytest.fixture
def many_links(create_link: Callable[..., URL]) -> list[URL]:
    """Набор ссылок, который не помещается на страницу по умолчанию"""
    return [create_link() for _ in range(15)]
