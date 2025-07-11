from datetime import UTC, datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from app.enums.speaker import SpeakerType
from app.models.camel_case import CamelModel

if TYPE_CHECKING:
    from app.models.session import Session


class SessionTurn(CamelModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key='session.id', ondelete='CASCADE')
    speaker: SpeakerType
    start_offset_ms: int
    end_offset_ms: int
    full_audio_start_offset_ms: int = Field(default=0)
    text: str
    audio_uri: str
    ai_emotion: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    session: Optional['Session'] = Relationship(back_populates='session_turns')
