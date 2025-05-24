from pydantic import BaseModel, Field
from typing import List


class TrainingCaseBase(BaseModel):
    category: str = Field(..., description="Training category")
    goal: str = Field(..., description="Training goal")
    context: str = Field(..., description="Training context")
    other_party: str = Field(..., description="Persona to speak with")


class ObjectiveRequest(TrainingCaseBase):
    num_objectives: int = Field(..., gt=0, description="Number of objectives to generate")


class KeyConceptRequest(TrainingCaseBase):
    pass  # Request for generating key concepts, inherits all fields from TrainingCaseBase


class ChecklistRequest(TrainingCaseBase):
    num_checkpoints: int = Field(..., gt=0, description="Number of checklist items to return")


class StringListResponse(BaseModel):
    items: List[str] = Field(..., description="List of generated text items")


class TextSection(BaseModel):
    title: str
    body: str


class ConceptOutput(BaseModel):
    header: str
    situation: str
    behavior: str
    impacts: str
    text: List[TextSection]
