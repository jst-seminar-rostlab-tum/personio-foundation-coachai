from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Annotated

from ..database import get_session
from ..models.language_model import LanguageModel, LanguageCreate, LanguageRead

router = APIRouter(prefix="/language", tags=["Language"])


@router.post("/", response_model=LanguageRead)
def create_language(
    language: LanguageCreate, session: Annotated[Session, Depends(get_session)]
) -> LanguageModel:
    """
    Create a new language.
    """
    # Check if the language code already exists
    existing_language = session.exec(
        select(LanguageModel).where(LanguageModel.code == language.code)
    ).first()
    if existing_language:
        raise HTTPException(status_code=400, detail="Language code must be unique")

    # Convert LanguageCreate to LanguageModel
    db_language = LanguageModel(**language.dict())
    session.add(db_language)
    session.commit()
    session.refresh(db_language)
    return db_language


@router.get("/", response_model=list[LanguageRead])
def read_languages(
    session: Annotated[Session, Depends(get_session)], skip: int = 0, limit: int = 100
) -> list[LanguageRead]:
    """
    Retrieve a list of languages.
    """
    statement = select(LanguageModel).offset(skip).limit(limit)
    languages = session.exec(statement).all()
    return languages