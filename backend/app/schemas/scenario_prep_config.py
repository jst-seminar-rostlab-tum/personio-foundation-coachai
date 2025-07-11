from pydantic import RootModel

from app.enums.language import LanguageCode
from app.models.camel_case import CamelModel
from app.schemas.scenario_preparation import KeyConceptResponse, StringListResponse


class ScenarioPrepSystemPromptSet(CamelModel):
    objectives: str
    checklist: str
    key_concepts: str


class ScenarioPrepMockSet(CamelModel):
    objectives: StringListResponse
    checklist: StringListResponse
    key_concepts: KeyConceptResponse


class ScenarioPrepLanguageSettings(CamelModel):
    system_prompts: ScenarioPrepSystemPromptSet
    mocks: ScenarioPrepMockSet


class ScenarioPrepConfig(RootModel[dict[LanguageCode, ScenarioPrepLanguageSettings]]):
    pass
