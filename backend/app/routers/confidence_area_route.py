from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_db_session
from app.models.confidence_area import ConfidenceArea, ConfidenceAreaCreate, ConfidenceAreaRead

router = APIRouter(prefix='/confidence-areas', tags=['Confidence Areas'])


@router.get('/', response_model=list[ConfidenceAreaRead])
def get_confidence_areas(
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> list[ConfidenceArea]:
    """
    Retrieve all confidence areas.
    """
    statement = select(ConfidenceArea)
    results = db_session.exec(statement).all()
    return list(results)


@router.post('/', response_model=ConfidenceAreaRead)
def create_confidence_area(
    confidence_area: ConfidenceAreaCreate, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> ConfidenceArea:
    """
    Create a new confidence area.
    """
    new_area = ConfidenceArea(**confidence_area.dict())
    db_session.add(new_area)
    db_session.commit()
    db_session.refresh(new_area)
    return new_area


@router.put('/{area_id}', response_model=ConfidenceAreaRead)
def update_confidence_area(
    area_id: UUID,
    updated_data: ConfidenceAreaCreate,
    db_session: Annotated[DBSession, Depends(get_db_session)],
) -> ConfidenceArea:
    """
    Update an existing confidence area.
    """
    area = db_session.get(ConfidenceArea, area_id)
    if not area:
        raise HTTPException(status_code=404, detail='Confidence area not found')
    for key, value in updated_data.dict().items():
        setattr(area, key, value)
    db_session.add(area)
    db_session.commit()
    db_session.refresh(area)
    return area


@router.delete('/{area_id}', response_model=dict)
def delete_confidence_area(
    area_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> dict:
    """
    Delete a confidence area.
    """
    area = db_session.get(ConfidenceArea, area_id)
    if not area:
        raise HTTPException(status_code=404, detail='Confidence area not found')
    db_session.delete(area)
    db_session.commit()
    return {'message': 'Confidence area deleted successfully'}
