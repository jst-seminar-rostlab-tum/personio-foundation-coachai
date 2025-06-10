from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import select

from app.database import get_db_session
from app.models.language import Language, LanguageCreate, LanguageRead

router = APIRouter(prefix='/language', tags=['Language'])


@router.post('/', response_model=LanguageRead)
def create_language(
    language: LanguageCreate, db_session: Annotated[DBSession, Depends(get_db_session)]
) -> Language:
    """
    Create a new language.
    """
    # Check if the language code already exists
    existing_language = db_session.exec(
        select(Language).where(Language.code == language.code)
    ).first()
    if existing_language:
        raise HTTPException(status_code=400, detail='Language code must be unique')

    # Convert LanguageCreate to Language
    db_language = Language(**language.dict())
    db_session.add(db_language)
    db_session.commit()
    db_session.refresh(db_language)
    return db_language


@router.get('/', response_model=list[LanguageRead])
def read_languages(
    db_session: Annotated[DBSession, Depends(get_db_session)], skip: int = 0, limit: int = 100
) -> list[Language]:
    """
    Retrieve a list of languages.
    """
    statement = select(Language).offset(skip).limit(limit)
    languages = db_session.exec(statement).all()
    return list(languages)
