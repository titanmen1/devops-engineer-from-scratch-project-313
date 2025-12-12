from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repository import URLRepository, URLRepositoryProtocol


async def get_url_repository(
    session: AsyncSession = Depends(get_session),
) -> URLRepositoryProtocol:
    """Dependency для получения экземпляра URLRepository"""
    return URLRepository(session)
