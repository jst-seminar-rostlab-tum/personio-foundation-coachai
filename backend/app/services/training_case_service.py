from uuid import uuid4

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.training_case import TrainingCase, TrainingCaseCreate


def create_training_case(training_case_data: TrainingCaseCreate, session: Session) -> TrainingCase:
    """
    Create TrainingCase
    """
    training_case_id = training_case_data.id or uuid4()
    language_code = training_case_data.language_code or 'en'

    if language_code not in ['en', 'de']:
        raise HTTPException(status_code=400, detail="Language code must be 'en' or 'de'.")

    stmt = select(TrainingCase).where(
        TrainingCase.id == training_case_id,
        TrainingCase.language_code == language_code
    )
    existing_case = session.exec(stmt).first()

    if existing_case:
        raise HTTPException(status_code=400,
                            detail="Training case with this ID and language already exists.")

    # Create a new TrainingCase instance
    db_case = TrainingCase(
        id=training_case_id,
        language_code=language_code,
        user_id=training_case_data.user_id,
        category_id=training_case_data.category_id,
        custom_category_label=training_case_data.custom_category_label,
        context=training_case_data.context,
        goal=training_case_data.goal,
        other_party=training_case_data.other_party,
        difficulty_id=training_case_data.difficulty_id,
        tone=training_case_data.tone,
        complexity=training_case_data.complexity,
        status=training_case_data.status,
    )
    session.add(db_case)
    session.commit()
    session.refresh(db_case)
    return db_case
