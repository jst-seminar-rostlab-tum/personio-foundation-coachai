from sqlmodel import Session as DBSession

from app.models.training_case import TrainingCase, TrainingCaseCreate


def create_training_case(
    training_case_data: TrainingCaseCreate, db_session: DBSession
) -> TrainingCase:
    """
    Create TrainingCase
    """
    db_case = TrainingCase(**training_case_data.model_dump())
    db_session.add(db_case)
    db_session.commit()
    db_session.refresh(db_case)
    return db_case
