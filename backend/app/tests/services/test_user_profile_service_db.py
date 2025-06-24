# backend/app/tests/services/test_user_profile_service.py

from collections.abc import Generator
from typing import Any
from uuid import uuid4

import pytest
from sqlalchemy import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.models.language import LanguageCode
from app.models.user_profile import (
    AccountRole,
    Experience,
    PreferredLearningStyle,
    ProfessionalRole,
    UserProfile,
)
from app.services.user_profile_service import delete_user_profile


@pytest.fixture
def test_engine() -> Engine:
    engine = create_engine('sqlite://', echo=False)
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(test_engine: Engine) -> Generator[Session, Any, None]:
    with Session(test_engine) as session:
        yield session


def test_delete_user_profile_success(db_session: Session) -> None:
    user_id = uuid4()
    user = UserProfile(
        id=user_id,
        full_name='Test User',
        email='test@example.com',
        phone_number='1234567890',
        preferred_language_code=LanguageCode.en,
        experience=Experience.beginner,
        preferred_learning_style=PreferredLearningStyle.visual,
        account_role=AccountRole.user,
        professional_role=ProfessionalRole.hr_professional,
    )
    db_session.add(user)
    db_session.commit()

    delete_user_profile(user_id, db_session=db_session)

    result = db_session.get(UserProfile, user_id)
    assert result is None


def test_delete_user_profile_not_found(db_session: Session) -> None:
    nonexistent_id = uuid4()

    with pytest.raises(Exception) as exc_info:
        delete_user_profile(user_id=nonexistent_id, db_session=db_session)

    assert exc_info.value.status_code == 404
