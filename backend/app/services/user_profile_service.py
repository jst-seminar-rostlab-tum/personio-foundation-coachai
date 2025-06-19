from typing import Union
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session

from app.models.user_confidence_score import ConfidenceScoreRead
from app.models.user_profile import (
    UserProfile,
    UserProfileExtendedRead,
    UserProfileRead,
    UserProfileReplace,
    UserProfileUpdate,
)
from app.repositories.user_profile_repository import UserProfileRepository


class UserProfileService:
    def __init__(self, db: Session) -> None:
        self.repo: UserProfileRepository = UserProfileRepository(db)

    def get_profiles(
        self, detailed: bool
    ) -> Union[list[UserProfileRead], list[UserProfileExtendedRead]]:
        users: list[UserProfile] = self.repo.get_all()
        if detailed:
            return [self._to_extended(u) for u in users]
        return [self._to_read(u) for u in users]

    def get_profile(
        self, user_id: UUID, detailed: bool
    ) -> Union[UserProfileRead, UserProfileExtendedRead]:
        user: UserProfile | None = self.repo.get(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail='User not found')
        return self._to_extended(user) if detailed else self._to_read(user)

    def replace_profile(self, user_id: UUID, data: UserProfileReplace) -> UserProfileExtendedRead:
        user = self.repo.get(user_id)
        if user is None:
            raise HTTPException(404, 'User not found')
        user = self.repo.replace(user, data)
        return self._to_extended(user)

    def update_profile(self, user_id: UUID, data: UserProfileUpdate) -> UserProfileExtendedRead:
        user = self.repo.get(user_id)
        if user is None:
            raise HTTPException(404, 'User not found')
        updated_user = self.repo.update(user, data)
        return self._to_extended(updated_user)

    def delete_profile(self, user_id: UUID) -> dict[str, str]:
        self.repo.delete(user_id)
        return {'message': 'User profile deleted successfully'}

    def _to_read(self, u: UserProfile) -> UserProfileRead:
        return UserProfileRead.model_validate(u)

    def _to_extended(self, u: UserProfile) -> UserProfileExtendedRead:
        return UserProfileExtendedRead(
            **u.model_dump(),
            goals=[g.goal for g in u.user_goals],
            confidence_scores=[
                ConfidenceScoreRead(
                    confidence_area=cs.confidence_area,
                    score=cs.score,
                )
                for cs in u.user_confidence_scores
            ],
        )
