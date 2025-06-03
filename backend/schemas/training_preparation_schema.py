from pydantic import BaseModel, Field


class TrainingCaseBase(BaseModel):
    category: str = Field(..., description='Training category')
    goal: str = Field(..., description='Training goal')
    context: str = Field(..., description='Training context')
    other_party: str = Field(..., description='Persona to speak with')


class ObjectiveRequest(TrainingCaseBase):
    num_objectives: int = Field(..., gt=0, description='Number of objectives to generate')


class KeyConceptRequest(TrainingCaseBase):
    pass  # Request for generating key concepts, inherits all fields from TrainingCaseBase


class ChecklistRequest(TrainingCaseBase):
    num_checkpoints: int = Field(..., gt=0, description='Number of checklist items to return')


class StringListResponse(BaseModel):
    items: list[str] = Field(..., description='List of generated text items')


class KeyConceptOutput(BaseModel):
    markdown: str


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
    key_concept: KeyConceptOutput = Field(..., description='Key concepts for the training case')
