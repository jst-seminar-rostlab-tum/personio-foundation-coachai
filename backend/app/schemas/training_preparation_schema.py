from pydantic import BaseModel, Field


class ConversationScenarioBase(BaseModel):
    category: str = Field(..., description='Training category')
    goal: str = Field(..., description='Training goal')
    context: str = Field(..., description='Training context')
    other_party: str = Field(..., description='Persona to speak with')


class ObjectiveRequest(ConversationScenarioBase):
    num_objectives: int = Field(..., gt=0, description='Number of objectives to generate')


class KeyConceptRequest(ConversationScenarioBase):
    pass  # Request for generating key concepts, inherits all fields from ConversationScenarioBase


class ChecklistRequest(ConversationScenarioBase):
    num_checkpoints: int = Field(..., gt=0, description='Number of checklist items to return')


class StringListResponse(BaseModel):
    items: list[str] = Field(..., description='List of generated text items')


class KeyConcept(BaseModel):
    header: str
    value: str


class KeyConceptOutput(BaseModel):
    items: list[KeyConcept]


class TrainingPreparationRequest(BaseModel):
    category: str = Field(..., description='Training category')
    goal: str = Field(..., description='Training goal')
    context: str = Field(..., description='Training context')
    other_party: str = Field(..., description='Persona to speak with')

    num_objectives: int = Field(3, gt=0, description='Number of objectives to generate')
    num_checkpoints: int = Field(5, gt=0, description='Number of checklist items to generate')


class TrainingPreparationResponse(BaseModel):
    objectives: StringListResponse = Field(..., description='List of training objectives')
    checklist: StringListResponse = Field(..., description='List of training checklist items')
    key_concept: KeyConceptOutput = Field(
        ..., description='Key concepts for the conversation scenario'
    )
