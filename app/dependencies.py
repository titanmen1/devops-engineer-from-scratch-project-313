from fastapi import Depends
from sqlmodel import Session

from app.database import get_session
from app.repository import URLRepository, URLRepositoryProtocol


def get_url_repository(
    session: Session = Depends(get_session),
) -> URLRepositoryProtocol:
    """Dependency для получения экземпляра URLRepository"""
    return URLRepository(session)
