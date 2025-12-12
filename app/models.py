from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class URLBase(SQLModel):
    original_url: str = Field(max_length=2048)


class URL(URLBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    short_name: str = Field(unique=True, index=True, max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)
