"""Pydantic schema definitions for scenario prep config."""

from pydantic import RootModel

from app.enums.language import LanguageCode
from app.models.camel_case import CamelModel
from app.schemas.scenario_preparation import KeyConceptsRead, StringListRead


class ScenarioPrepSystemPromptSet(CamelModel):
    """Schema for scenario prep system prompt set."""

    objectives: str
    checklist: str
    key_concepts: str


class ScenarioPrepMockSet(CamelModel):
    """Schema for scenario prep mock set."""

    objectives: StringListRead
    checklist: StringListRead
    key_concepts: KeyConceptsRead


class ScenarioPrepLanguageSettings(CamelModel):
    """Schema for scenario prep language settings."""

    system_prompts: ScenarioPrepSystemPromptSet
    mocks: ScenarioPrepMockSet


class ScenarioPrepConfigRead(RootModel[dict[LanguageCode, ScenarioPrepLanguageSettings]]):
    """Schema for scenario prep config read."""

    pass
