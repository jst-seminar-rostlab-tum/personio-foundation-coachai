from datetime import datetime
from uuid import UUID

from sqlmodel import JSON, Column, Field

from app.enums.difficulty_level import DifficultyLevel
from app.enums.language import LanguageCode
from app.enums.scenario_preparation_status import ScenarioPreparationStatus
from app.models.camel_case import CamelModel

# Schemas for scenario preparation


# Schema for genarating objectives / goals
class ObjectivesCreate(CamelModel):
    category: str
    persona: str
    situational_facts: str
    language_code: LanguageCode = Field(
        default=LanguageCode.en, description='Language code for the scenario preparation'
    )
    num_objectives: int = Field(..., gt=0, description='Number of objectives to generate')


# Schema for generating key concepts
class KeyConceptsCreate(CamelModel):
    category: str
    persona: str
    situational_facts: str
    language_code: LanguageCode = Field(
        default=LanguageCode.en, description='Language code for the scenario preparation'
    )


# Schema for generating a checklist
class ChecklistCreate(CamelModel):
    category: str
    persona: str
    situational_facts: str
    language_code: LanguageCode = Field(
        default=LanguageCode.en, description='Language code for the scenario preparation'
    )
    num_checkpoints: int = Field(..., gt=0, description='Number of checklist items to return')


# Response schema for a list of strings --> needed to return generated text in a given format
class StringListRead(CamelModel):
    items: list[str]


# Response schema for key concepts
class KeyConcept(CamelModel):
    header: str
    value: str


class KeyConceptsRead(CamelModel):
    items: list[KeyConcept]


# Schema for creating a new ScenarioPreparation
class ScenarioPreparationCreate(CamelModel):
    category: str
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
    documents: list[dict] = Field(default_factory=list, sa_column=Column(JSON))
    key_concepts: list[KeyConcept] = Field(default_factory=list, sa_column=Column(JSON))
    prep_checklist: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: ScenarioPreparationStatus
    category_name: str | None = None
    category_id: str | None = None
    persona_name: str
    persona: str
    difficulty_level: DifficultyLevel
    situational_facts: str
    created_at: datetime
    updated_at: datetime
