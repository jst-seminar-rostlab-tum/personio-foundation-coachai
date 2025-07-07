from datetime import datetime
from uuid import UUID

from sqlmodel import JSON, Column, Field

from app.models.camel_case import CamelModel
from app.models.language import LanguageCode
from app.models.scenario_preparation import ScenarioPreparationStatus

# Schemas for scenario preparation


# Schema for genarating objectives / goals
class ObjectiveRequest(CamelModel):
    category: str = Field(..., description='Training category')
    persona: str
    situational_facts: str
    language_code: LanguageCode = Field(
        default=LanguageCode.en, description='Language code for the scenario preparation'
    )
    num_objectives: int = Field(..., gt=0, description='Number of objectives to generate')


# Schema for generating key concepts
class KeyConceptRequest(CamelModel):
    category: str = Field(..., description='Training category')
    persona: str
    situational_facts: str
    language_code: LanguageCode = Field(
        default=LanguageCode.en, description='Language code for the scenario preparation'
    )


# Schema for generating a checklist
class ChecklistRequest(CamelModel):
    category: str = Field(..., description='Training category')
    persona: str
    situational_facts: str
    language_code: LanguageCode = Field(
        default=LanguageCode.en, description='Language code for the scenario preparation'
    )
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


# Schema for creating a new ScenarioPreparation
class ScenarioPreparationCreate(CamelModel):
    category: str = Field(..., description='Training category')
    persona: str
    situational_facts: str
    language_code: LanguageCode = Field(
        default=LanguageCode.en, description='Language code for the scenario preparation'
    )
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
    category_name: str | None = None
    persona: str
    situational_facts: str
    created_at: datetime
    updated_at: datetime
