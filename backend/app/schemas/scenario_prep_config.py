from pydantic import RootModel

from app.enums.language import LanguageCode
from app.models.camel_case import CamelModel
from app.schemas.scenario_preparation import KeyConceptsRead, StringListRead


class ScenarioPrepSystemPromptSet(CamelModel):
    objectives: str
    checklist: str
    key_concepts: str


class ScenarioPrepMockSet(CamelModel):
    objectives: StringListRead
    checklist: StringListRead
    key_concepts: KeyConceptsRead


class ScenarioPrepLanguageSettings(CamelModel):
    system_prompts: ScenarioPrepSystemPromptSet
    mocks: ScenarioPrepMockSet


class ScenarioPrepConfigRead(RootModel[dict[LanguageCode, ScenarioPrepLanguageSettings]]):
    pass
