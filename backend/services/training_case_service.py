from sqlmodel import Session

from ..models import TrainingCase, TrainingCaseCreate


def create_training_case(training_case_data: TrainingCaseCreate, session: Session) -> TrainingCase:
    """
    Create TrainingCase
    """
    db_case = TrainingCase(**training_case_data.dict())
    session.add(db_case)
    session.commit()
    session.refresh(db_case)
    return db_case
