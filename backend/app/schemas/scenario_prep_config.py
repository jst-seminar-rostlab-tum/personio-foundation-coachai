from pydantic import RootModel

from app.enums.language import LanguageCode
from app.models.camel_case import CamelModel
<<<<<<< HEAD
from app.schemas.scenario_preparation import KeyConceptResponse, StringListResponse
=======
from app.models.language import LanguageCode
from app.schemas.scenario_preparation import KeyConceptsRead, StringListRead
>>>>>>> 1dc3d9f07749118303eae86df64f8377fce53210


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
