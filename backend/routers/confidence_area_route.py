from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from ..database import get_session
from ..models.confidence_area import ConfidenceArea, ConfidenceAreaCreate, ConfidenceAreaRead

router = APIRouter(prefix='/confidence-areas', tags=['Confidence Areas'])


@router.get('/', response_model=list[ConfidenceAreaRead])
def get_confidence_areas(session: Annotated[Session, Depends(get_session)]) -> list[ConfidenceArea]:
    """
    Retrieve all confidence areas.
    """
    statement = select(ConfidenceArea)
    results = session.exec(statement).all()
    return list(results)


@router.post('/', response_model=ConfidenceAreaRead)
def create_confidence_area(
    confidence_area: ConfidenceAreaCreate, session: Annotated[Session, Depends(get_session)]
) -> ConfidenceArea:
    """
    Create a new confidence area.
    """
    new_area = ConfidenceArea(**confidence_area.dict())
    session.add(new_area)
    session.commit()
    session.refresh(new_area)
    return new_area


@router.put('/{area_id}', response_model=ConfidenceAreaRead)
def update_confidence_area(
    area_id: UUID,
    updated_data: ConfidenceAreaCreate,
    session: Annotated[Session, Depends(get_session)],
) -> ConfidenceArea:
    """
    Update an existing confidence area.
    """
    area = session.get(ConfidenceArea, area_id)
    if not area:
        raise HTTPException(status_code=404, detail='Confidence area not found')
    for key, value in updated_data.dict().items():
        setattr(area, key, value)
    session.add(area)
    session.commit()
    session.refresh(area)
    return area


@router.delete('/{area_id}', response_model=dict)
def delete_confidence_area(
    area_id: UUID, session: Annotated[Session, Depends(get_session)]
) -> dict:
    """
    Delete a confidence area.
    """
    area = session.get(ConfidenceArea, area_id)
    if not area:
        raise HTTPException(status_code=404, detail='Confidence area not found')
    session.delete(area)
    session.commit()
    return {'message': 'Confidence area deleted successfully'}
