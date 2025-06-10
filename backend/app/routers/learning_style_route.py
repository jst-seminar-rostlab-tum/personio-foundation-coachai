from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_db_session
from app.models.learning_style import LearningStyle, LearningStyleCreate, LearningStyleRead

router = APIRouter(prefix='/learning-styles', tags=['Learning Styles'])


@router.get('/', response_model=list[LearningStyleRead])
def get_learning_styles(
        db_session: Annotated[DBSession, Depends(get_db_session)],
        lang: str = Query(default="en", description="Requested language code")
) -> list[LearningStyle]:
    """
    Retrieve all learning styles.
    """
    stmt = select(LearningStyle).where(LearningStyle.language_code.in_([lang, "en"]))
    results = db_session.exec(stmt).all()

    styles_by_id = {}
    for style in results:
        if style.id not in styles_by_id or style.language_code == lang:
            styles_by_id[style.id] = style

    return list(styles_by_id.values())


@router.post('/', response_model=LearningStyleRead)
def create_learning_style(
        learning_style: LearningStyleCreate,
        db_session: Annotated[DBSession, Depends(get_db_session)]
) -> LearningStyle:
    """
    Create a new learning style.
    """
    style_id = learning_style.id or uuid4()
    lang_code = learning_style.language_code or "en"

    if lang_code not in ["en", "de"]:
        raise HTTPException(status_code=400, detail="Unsupported language code.")

    # Check if record already exists
    stmt = select(LearningStyle).where(
        LearningStyle.id == style_id,
        LearningStyle.language_code == lang_code
    )
    existing = db_session.exec(stmt).first()
    if existing:
        raise HTTPException(status_code=400,
                            detail="LearningStyle with this language already exists.")

    new_style = LearningStyle(
        id=style_id,
        language_code=lang_code,
        label=learning_style.label,
        description=learning_style.description
    )

    db_session.add(new_style)
    db_session.commit()
    db_session.refresh(new_style)
    return new_style

@router.put('/{learning_style_id}', response_model=LearningStyleRead)
def update_learning_style(
        learning_style_id: UUID,
        updated_data: LearningStyleCreate,
        db_session: Annotated[DBSession, Depends(get_db_session)],
        lang: str = Query(default="en")
) -> LearningStyle:
    """
    Update an existing learning style.
    """
    stmt = select(LearningStyle).where(
        LearningStyle.id == learning_style_id,
        LearningStyle.language_code == lang
    )
    style = db_session.exec(stmt).first()
    if not style:
        raise HTTPException(status_code=404, detail='Learning style not found')
    for key, value in updated_data.model_dump().items():
        if key != "id":
            setattr(style, key, value)
    db_session.commit()
    db_session.refresh(style)
    return style

@router.delete('/{learning_style_id}', response_model=dict)
def delete_learning_style(
        learning_style_id: UUID, db_session: Annotated[DBSession, Depends(get_db_session)],
        lang: str = Query(default="en", description="Requested language code")
) -> dict:
    """
    Delete a learning style.
    """
    stmt = select(LearningStyle).where(
        LearningStyle.id == learning_style_id,
        LearningStyle.language_code == lang
    )
    style = db_session.exec(stmt).first()
    if not style:
        raise HTTPException(status_code=404, detail='Learning style not found')
    db_session.delete(style)
    db_session.commit()
    return {'message': 'Learning style deleted successfully'}
