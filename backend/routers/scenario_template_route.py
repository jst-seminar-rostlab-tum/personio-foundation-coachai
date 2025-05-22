from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models.conversation_category_model import ConversationCategory
from ..models.language_model import LanguageModel
from ..models.scenario_template_model import (
    ScenarioTemplateCreate,
    ScenarioTemplateModel,
    ScenarioTemplateRead,
)

router = APIRouter(prefix='/scenario-templates', tags=['Scenario Templates'])


@router.get('/', response_model=list[ScenarioTemplateRead])
def get_scenario_templates(
    session: Annotated[Session, Depends(get_session)],
) -> list[ScenarioTemplateModel]:
    """
    Retrieve all scenario templates.
    """
    statement = select(ScenarioTemplateModel)
    templates = session.exec(statement).all()
    return list(templates)


@router.post('/', response_model=ScenarioTemplateRead)
def create_scenario_template(
    template: ScenarioTemplateCreate, session: Annotated[Session, Depends(get_session)]
) -> ScenarioTemplateModel:
    """
    Create a new scenario template.
    """
    # Validate foreign keys
    if template.category_id:
        category = session.get(ConversationCategory, template.category_id)
        if not category:
            raise HTTPException(status_code=404, detail='Category not found')

    language = session.exec(
        select(LanguageModel).where(LanguageModel.code == template.language_code)
    ).first()
    if not language:
        raise HTTPException(status_code=404, detail='Language not found')

    db_template = ScenarioTemplateModel(**template.dict())
    session.add(db_template)
    session.commit()
    session.refresh(db_template)
    return db_template


@router.put('/{template_id}', response_model=ScenarioTemplateRead)
def update_scenario_template(
    template_id: UUID,
    updated_data: ScenarioTemplateCreate,
    session: Annotated[Session, Depends(get_session)],
) -> ScenarioTemplateModel:
    """
    Update an existing scenario template.
    """
    template = session.get(ScenarioTemplateModel, template_id)
    if not template:
        raise HTTPException(status_code=404, detail='Scenario template not found')

    # Validate foreign keys
    if updated_data.category_id:
        category = session.get(ConversationCategory, updated_data.category_id)
        if not category:
            raise HTTPException(status_code=404, detail='Category not found')

    if updated_data.language_code:
        language = session.exec(
            select(LanguageModel).where(LanguageModel.code == updated_data.language_code)
        ).first()
        if not language:
            raise HTTPException(status_code=404, detail='Language not found')

    for key, value in updated_data.dict().items():
        setattr(template, key, value)

    session.add(template)
    session.commit()
    session.refresh(template)
    return template


@router.delete('/{template_id}', response_model=dict)
def delete_scenario_template(
    template_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a scenario template.
    """
    template = session.get(ScenarioTemplateModel, template_id)
    if not template:
        raise HTTPException(status_code=404, detail='Scenario template not found')

    session.delete(template)
    session.commit()
    return {'message': 'Scenario template deleted successfully'}
