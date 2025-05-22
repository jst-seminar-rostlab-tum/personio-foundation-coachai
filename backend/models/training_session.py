from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import event
from sqlmodel import JSON, Column, Field, Relationship, SQLModel


class TrainingSession(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    case_id: UUID = Field(foreign_key="trainingcase.id")  # Foreign key to TrainingCase
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    language_code: str = Field(foreign_key="language.code")  # Foreign key to LanguageModel
    ai_persona: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    case: Optional["TrainingCase"] = Relationship(back_populates="sessions")
    language: Optional["Language"] = Relationship()  # Relationship to Language
    conversation_turns: List["ConversationTurn"] = Relationship(back_populates="session")
    feedback: Optional["TrainingSessionFeedback"] = Relationship(back_populates="session")
    ratings: List["Rating"] = Relationship(back_populates="session")

    # Automatically update `updated_at` before an update
@event.listens_for(TrainingSession, "before_update")
def update_timestamp(mapper, connection, target) -> None:
    target.updated_at = datetime.utcnow()
# Schema for creating a new TrainingSession
class TrainingSessionCreate(SQLModel):
    case_id: UUID
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    language_code: str
    ai_persona: dict = Field(default_factory=dict, sa_column=Column(JSON))

# Schema for reading TrainingSession data
class TrainingSessionRead(SQLModel):
    id: UUID
    case_id: UUID
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    language_code: str
    ai_persona: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime
    updated_at: datetime