"""Pydantic schema definitions for user export."""

from typing import Any

from pydantic import BaseModel


class ExportUserProfile(BaseModel):
    """Schema for export user profile."""

    user_id: str
    full_name: str
    email: str
    phone_number: str
    preferred_language_code: str
    experience: str
    preferred_learning_style: str
    updated_at: str
    last_logged_in: str
    store_conversations: bool
    account_role: str
    professional_role: str
    current_streak_days: int
    total_sessions: int
    training_time: float
    score_sum: float
    goals_achieved: int
    scenario_advice: dict
    sessions_created_today: int
    last_session_date: str
    daily_session_limit: int | None
    organization_name: str | None


class ExportUserGoal(BaseModel):
    """Schema for export user goal."""

    goal: str
    updated_at: str | None


class ExportConfidenceScore(BaseModel):
    """Schema for export confidence score."""

    confidence_area: str
    score: int
    updated_at: str | None


class ExportConversationScenario(BaseModel):
    """Schema for export conversation scenario."""

    id: str
    category_id: str | None
    custom_category_label: str | None
    language_code: str
    persona_name: str
    persona: str
    situational_facts: str
    difficulty_level: str
    status: str
    created_at: str | None
    updated_at: str | None


class ExportScenarioPreparation(BaseModel):
    """Schema for export scenario preparation."""

    id: str
    scenario_id: str
    objectives: list[str]
    key_concepts: list[dict[str, Any]]
    prep_checklist: list[str]
    status: str
    created_at: str | None
    updated_at: str | None


class ExportSession(BaseModel):
    """Schema for export session."""

    id: str
    scenario_id: str
    scheduled_at: str | None
    started_at: str | None
    ended_at: str | None
    status: str
    created_at: str | None
    updated_at: str | None


class ExportSessionTurn(BaseModel):
    """Schema for export session turn."""

    id: str
    session_id: str
    speaker: str
    start_offset_ms: int
    end_offset_ms: int
    text: str
    audio_uri: str
    ai_emotion: str | None = None
    created_at: str | None


class ExportSessionFeedback(BaseModel):
    """Schema for export session feedback."""

    id: str
    session_id: str
    scores: dict[str, Any]
    tone_analysis: dict[str, Any]
    overall_score: float
    speak_time_percent: float
    questions_asked: int
    session_length_s: int
    goals_achieved: list[str]
    example_positive: list[dict[str, Any]]
    example_negative: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    status: str
    created_at: str | None
    updated_at: str | None


class ExportReview(BaseModel):
    """Schema for export review."""

    id: str
    session_id: str | None
    rating: int
    comment: str
    created_at: str | None


class UserDataExport(BaseModel):
    """Schema for user data export."""

    profile: ExportUserProfile
    goals: list[ExportUserGoal]
    confidence_scores: list[ExportConfidenceScore]
    scenarios: list[ExportConversationScenario]
    scenario_preparations: list[ExportScenarioPreparation]
    sessions: list[ExportSession]
    session_turns: list[ExportSessionTurn]
    session_feedback: list[ExportSessionFeedback]
    reviews: list[ExportReview]
