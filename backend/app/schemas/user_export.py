from typing import Any, Optional

from pydantic import BaseModel


class ExportUserProfile(BaseModel):
    user_id: str
    full_name: str
    email: str
    phone_number: Optional[str]
    preferred_language_code: str
    account_role: str
    professional_role: str
    experience: str
    preferred_learning_style: str
    updated_at: Optional[str]
    store_conversations: bool
    total_sessions: int
    training_time: float
    current_streak_days: int
    score_sum: float
    goals_achieved: int
    num_remaining_daily_sessions: int


class ExportUserGoal(BaseModel):
    goal: str
    updated_at: Optional[str]


class ExportConfidenceScore(BaseModel):
    confidence_area: str
    score: int
    updated_at: Optional[str]


class ExportConversationScenario(BaseModel):
    id: str
    category_id: Optional[str]
    custom_category_label: Optional[str]
    language_code: str
    persona: str
    situational_facts: str
    difficulty_level: str
    status: str
    created_at: Optional[str]
    updated_at: Optional[str]


class ExportScenarioPreparation(BaseModel):
    id: str
    scenario_id: str
    objectives: list[str]
    key_concepts: list[dict[str, Any]]
    prep_checklist: list[str]
    status: str
    created_at: Optional[str]
    updated_at: Optional[str]


class ExportSession(BaseModel):
    id: str
    scenario_id: str
    scheduled_at: Optional[str]
    started_at: Optional[str]
    ended_at: Optional[str]
    status: str
    created_at: Optional[str]
    updated_at: Optional[str]


class ExportSessionTurn(BaseModel):
    id: str
    session_id: str
    speaker: str
    start_offset_ms: int
    end_offset_ms: int
    text: str
    audio_uri: str
    ai_emotion: str
    created_at: Optional[str]


class ExportSessionFeedback(BaseModel):
    id: str
    session_id: str
    scores: dict[str, Any]
    tone_analysis: dict[str, Any]
    overall_score: float
    transcript_uri: str
    speak_time_percent: float
    questions_asked: int
    session_length_s: int
    goals_achieved: list[str]
    example_positive: list[dict[str, Any]]
    example_negative: list[dict[str, Any]]
    recommendations: list[dict[str, Any]]
    status: str
    created_at: Optional[str]
    updated_at: Optional[str]


class ExportReview(BaseModel):
    id: str
    session_id: Optional[str]
    rating: int
    comment: str
    created_at: Optional[str]


class UserDataExport(BaseModel):
    profile: ExportUserProfile
    goals: list[ExportUserGoal]
    confidence_scores: list[ExportConfidenceScore]
    scenarios: list[ExportConversationScenario]
    scenario_preparations: list[ExportScenarioPreparation]
    sessions: list[ExportSession]
    session_turns: list[ExportSessionTurn]
    session_feedback: list[ExportSessionFeedback]
    reviews: list[ExportReview]
