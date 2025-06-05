from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.user_confidence_score import UserConfidenceScore


class ConfidenceArea(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    label: str
    description: str
    min_value: int
    max_value: int
    min_label: str
    max_label: str
    user_confidence_scores: list['UserConfidenceScore'] = Relationship(
        back_populates='confidence_area', cascade_delete=True
    )


class ConfidenceAreaCreate(SQLModel):
    label: str
    description: str
    min_value: int
    max_value: int
    min_label: str
    max_label: str


class ConfidenceAreaRead(SQLModel):
    id: UUID
    label: str
    description: str
    min_value: int
    max_value: int
    min_label: str
    max_label: str
