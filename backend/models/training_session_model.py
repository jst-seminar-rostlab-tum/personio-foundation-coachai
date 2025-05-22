from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.models.conversation_turn_model import ConversationTurnModel
    from backend.models.language_model import LanguageModel
    from backend.models.rating_model import RatingModel
    from backend.models.training_case_model import TrainingCaseModel
    from backend.models.training_session_feedback_model import TrainingSessionFeedbackModel


class TrainingSessionModel(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    case_id: UUID = Field(foreign_key='trainingcasemodel.id')  # Foreign key to TrainingCase
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    language_code: str = Field(foreign_key='languagemodel.code')  # Foreign key to LanguageModel
    ai_persona: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    case: Optional['TrainingCaseModel'] = Relationship(back_populates='sessions')
    language: Optional['LanguageModel'] = Relationship()  # Relationship to LanguageModel
    conversation_turns: list['ConversationTurnModel'] = Relationship(back_populates='session')
    feedback: Optional['TrainingSessionFeedbackModel'] = Relationship(back_populates='session')
    ratings: list['RatingModel'] = Relationship(back_populates='session')


# Schema for creating a new TrainingSession
class TrainingSessionCreate(SQLModel):
    case_id: UUID
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    language_code: str
    ai_persona: str


# Schema for reading TrainingSession data
class TrainingSessionRead(SQLModel):
    id: UUID
    case_id: UUID
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    language_code: str
    ai_persona: str
    created_at: datetime
    updated_at: datetime
