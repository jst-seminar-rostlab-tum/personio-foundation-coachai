from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import JSON, Column, Field

from app.models.camel_case import CamelModel
from app.models.language import LanguageCode
from app.models.scenario_preparation import ScenarioPreparationStatus

# Schemas for scenario preparation requests


# The ConversationScenarioBase fields are used in various scenario preparation requests
# and are extended with other necessary information according to the request type
class ConversationScenarioBase(CamelModel):
    category: str = Field(..., description='Training category')
    goal: str = Field(..., description='Training goal')
    context: str = Field(..., description='Training context')
    other_party: str = Field(..., description='Persona to speak with')
    language_code: LanguageCode = Field(
        default=LanguageCode.en, description='Language code for the scenario preparation'
    )


# Schema for genarating objectives / goals
# --> extends ConversationScenarioBase
class ObjectiveRequest(ConversationScenarioBase):
    num_objectives: int = Field(..., gt=0, description='Number of objectives to generate')


# Schema for generating key concepts
# --> same fields as ConversationScenarioBase
class KeyConceptRequest(ConversationScenarioBase):
    pass


# Schema for generating a checklist
# --> extends ConversationScenarioBase
class ChecklistRequest(ConversationScenarioBase):
    num_checkpoints: int = Field(..., gt=0, description='Number of checklist items to return')


# Response schema for a list of strings
class StringListResponse(CamelModel):
    items: list[str] = Field(..., description='List of generated text items')


# Response schema for key concepts
class KeyConcept(CamelModel):
    header: str
    value: str


class KeyConceptResponse(CamelModel):
    items: list[KeyConcept]


# Schema for creating a new ScenarioPreparation --> extends ConversationScenarioBase
class ScenarioPreparationCreate(ConversationScenarioBase):
    num_objectives: int = Field(3, gt=0, description='Number of objectives to generate')
    num_checkpoints: int = Field(5, gt=0, description='Number of checklist items to generate')


# Schema for reading ScenarioPreparation data
class ScenarioPreparationRead(CamelModel):
    id: UUID
    scenario_id: UUID
    objectives: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    key_concepts: list[KeyConcept] = Field(default_factory=list, sa_column=Column(JSON))
    prep_checklist: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: ScenarioPreparationStatus
    category_name: Optional[str] = None
    context: Optional[str] = None
    goal: Optional[str] = None
    other_party: Optional[str] = None
    created_at: datetime
    updated_at: datetime
