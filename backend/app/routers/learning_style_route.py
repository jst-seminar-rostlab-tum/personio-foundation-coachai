from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.database import get_session
from app.models.learning_style import LearningStyle, LearningStyleCreate, LearningStyleRead

router = APIRouter(prefix='/learning-styles', tags=['Learning Styles'])


@router.get('/', response_model=list[LearningStyleRead])
def get_learning_styles(session: Annotated[Session, Depends(get_session)],
                        lang: str = Query(default="en", description="Requested language code")) -> \
list[LearningStyle]:
    stmt = select(LearningStyle).where(LearningStyle.language_code.in_([lang, "en"]))
    results = session.exec(stmt).all()

    styles_by_id = {}
    for style in results:
        if style.id not in styles_by_id or style.language_code == lang:
            styles_by_id[style.id] = style

    return list(styles_by_id.values())


@router.post('/', response_model=LearningStyleRead)
def create_learning_style(
        learning_style: LearningStyleCreate,
        session: Annotated[Session, Depends(get_session)]
) -> LearningStyle:
    style_id = learning_style.id or uuid4()
    lang_code = learning_style.language_code or "en"

    if lang_code not in ["en", "de"]:
        raise HTTPException(status_code=400, detail="Unsupported language code.")

    # Check if record already exists
    stmt = select(LearningStyle).where(
        LearningStyle.id == style_id,
        LearningStyle.language_code == lang_code
    )
    existing = session.exec(stmt).first()
    if existing:
        raise HTTPException(status_code=400,
                            detail="LearningStyle with this language already exists.")

    new_style = LearningStyle(
        id=style_id,
        language_code=lang_code,
        label=learning_style.label,
        description=learning_style.description
    )
    session.add(new_style)
    session.commit()
    session.refresh(new_style)
    return new_style


@router.put('/{learning_style_id}', response_model=LearningStyleRead)
def update_learning_style(
        learning_style_id: UUID,
        updated_data: LearningStyleCreate,
        session: Annotated[Session, Depends(get_session)],
        lang: str = Query(default="en")
) -> LearningStyle:
    stmt = select(LearningStyle).where(
        LearningStyle.id == learning_style_id,
        LearningStyle.language_code == lang
    )
    style = session.exec(stmt).first()
    if not style:
        raise HTTPException(status_code=404, detail='Learning style not found')
    for key, value in updated_data.model_dump().items():
        if key != "id":
            setattr(style, key, value)
    session.commit()
    session.refresh(style)
    return style


@router.delete('/{learning_style_id}', response_model=dict)
def delete_learning_style(
        learning_style_id: UUID, session: Annotated[Session, Depends(get_session)],
        lang: str = Query(default="en")
) -> dict:
    """
    Delete a learning style.
    """
    stmt = select(LearningStyle).where(
        LearningStyle.id == learning_style_id,
        LearningStyle.language_code == lang
    )
    style = session.exec(stmt).first()
    if not style:
        raise HTTPException(status_code=404, detail='Learning style not found')
    session.delete(style)
    session.commit()
    return {'message': 'Learning style deleted successfully'}
