"""Database model definitions for review."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.session import Session
    from app.models.user_profile import UserProfile


class Review(CamelModel, table=True):
    """Database model for review."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key='userprofile.id', ondelete='CASCADE')
    session_id: UUID | None = Field(foreign_key='session.id', default=None, ondelete='CASCADE')
    rating: int = Field(ge=1, le=5)
    comment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Relationships

    user_profile: 'UserProfile' = Relationship(back_populates='reviews')
    session: Optional['Session'] = Relationship(back_populates='session_review')
