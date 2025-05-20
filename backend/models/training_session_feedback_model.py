from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from uuid import uuid4, UUID
from enum import Enum
from typing import Optional

class FeedbackStatusEnum(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"

class TrainingSessionFeedbackModel(SQLModel, table=True):  # `table=True` makes it a database table
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="trainingsessionmodel.id")  # FK to TrainingSessionModel
    scores: int
    tone_analysis: str
    overall_score: int
    transcript_uri: str
    speak_time_percent: float
    questions_asked: int
    session_length_s: int
    goals_achieved: int
    examples_positive: str
    examples_negative: str
    recommendations: str
    status: FeedbackStatusEnum = Field(default=FeedbackStatusEnum.pending)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    session: Optional["TrainingSessionModel"] = Relationship(back_populates="feedback")

# Schema for creating a new TrainingSessionFeedback
class TrainingSessionFeedbackCreate(SQLModel):
    session_id: UUID
    scores: int
    tone_analysis: str
    overall_score: int
    transcript_uri: str
    speak_time_percent: float
    questions_asked: int
    session_length_s: int
    goals_achieved: int
    examples_positive: str
    examples_negative: str
    recommendations: str
    status: FeedbackStatusEnum = FeedbackStatusEnum.pending

# Schema for reading TrainingSessionFeedback data
class TrainingSessionFeedbackRead(SQLModel):
    id: UUID
    session_id: UUID
    scores: int
    tone_analysis: str
    overall_score: int
    transcript_uri: str
    speak_time_percent: float
    questions_asked: int
    session_length_s: int
    goals_achieved: int
    examples_positive: str
    examples_negative: str
    recommendations: str
    status: FeedbackStatusEnum
    created_at: datetime
    updated_at: datetime