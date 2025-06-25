from math import ceil
from typing import Union
from uuid import UUID

from fastapi import HTTPException
from sqlmodel import Session as DBSession
from sqlmodel import col, select

from app.models.user_confidence_score import UserConfidenceScore
from app.models.user_goal import Goal, UserGoal
from app.models.user_profile import UserProfile
from app.schemas.user_confidence_score import ConfidenceScoreRead
from app.schemas.user_profile import (
    PaginatedUserResponse,
    UserEmailRead,
    UserProfileExtendedRead,
    UserProfileRead,
    UserProfileReplace,
    UserProfileUpdate,
    UserStatisticsRead,
)


class UserService:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def _get_detailed_user_profile_response(self, user: UserProfile) -> UserProfileExtendedRead:
        return UserProfileExtendedRead(
            user_id=user.id,
            full_name=user.full_name,
            email=user.email,
            phone_number=user.phone_number,
            preferred_language_code=user.preferred_language_code,
            account_role=user.account_role,
            professional_role=user.professional_role,
            experience=user.experience,
            preferred_learning_style=user.preferred_learning_style,
            goals=[goal.goal for goal in user.user_goals],
            confidence_scores=[
                ConfidenceScoreRead(
                    confidence_area=cs.confidence_area,
                    score=cs.score,
                )
                for cs in user.user_confidence_scores
            ],
            updated_at=user.updated_at,
            store_conversations=user.store_conversations,
        )

    def _get_user_profile_response(self, user: UserProfile) -> UserProfileRead:
        return UserProfileRead(
            user_id=user.id,
            full_name=user.full_name,
            email=user.email,
            phone_number=user.phone_number,
            preferred_language_code=user.preferred_language_code,
            account_role=user.account_role,
            professional_role=user.professional_role,
            experience=user.experience,
            preferred_learning_style=user.preferred_learning_style,
            updated_at=user.updated_at,
            store_conversations=user.store_conversations,
        )

    def get_user_profiles(
        self, detailed: bool, page: int = 1, page_size: int = 10, email_substring: str | None = None
    ) -> PaginatedUserResponse:
        statement = select(UserProfile)
        if email_substring:
            statement = statement.where(col(UserProfile.email).like(f'%{email_substring}%'))

        statement = statement.order_by(col(UserProfile.updated_at).desc())

        total_users = len(self.db.exec(statement).all())
        if total_users == 0:
            raise HTTPException(
                status_code=404,
                detail='No user profiles found.',
            )

        total_pages = ceil(total_users / page_size)
        if page < 1 or page > total_pages:
            raise HTTPException(
                status_code=400,
                detail='Invalid page number.',
            )

        users = self.db.exec(statement.offset((page - 1) * page_size).limit(page_size)).all()

        if detailed:
            user_list = [self._get_detailed_user_profile_response(user) for user in users]
        else:
            user_list = [UserEmailRead(user_id=user.id, email=user.email) for user in users]

        return PaginatedUserResponse(
            page=page,
            limit=page_size,
            total_pages=total_pages,
            total_users=total_users,
            users=user_list,
        )

    def get_user_profile_by_id(
        self, user_id: UUID, detailed: bool
    ) -> Union[UserProfileRead, UserProfileExtendedRead]:
        user = self.db.get(UserProfile, user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail='User profile not found.',
            )

        if detailed:
            return self._get_detailed_user_profile_response(user)
        else:
            return self._get_user_profile_response(user)

    def get_user_statistics(self, user_id: UUID) -> UserStatisticsRead:
        user = self.db.get(UserProfile, user_id)
        if not user:
            raise HTTPException(
                status_code=404,
                detail='User profile not found.',
            )

        return UserStatisticsRead(
            total_sessions=user.total_sessions,
            training_time=user.training_time,
            current_streak_days=user.current_streak_days,
            average_score=user.average_score,
            goals_achieved=user.goals_achieved,
            # TODO: Uncomment and implement these fields when ready
            # performance_over_time=user.performance_over_time,
            # skills_performance=user.skills_performance
            # Mockked data for now
            performance_over_time=[72, 65, 70, 68, 74, 71, 78, 80, 69, 82],
            skills_performance={'structure': 85, 'empathy': 70, 'solutionFocus': 75, 'clarity': 75},
        )

    def _update_goals(self, user_id: UUID, goals: list[Goal]) -> None:
        # Clear existing goals
        statement = select(UserGoal).where(UserGoal.user_id == user_id)
        existing_goals = self.db.exec(statement).all()
        for goal in existing_goals:
            self.db.delete(goal)
        self.db.commit()

        # Add new goals
        for goal in goals:
            new_goal = UserGoal(user_id=user_id, goal=Goal(goal))
            self.db.add(new_goal)
        self.db.commit()

    def _update_confidence_scores(
        self, user_id: UUID, confidence_scores: list[ConfidenceScoreRead]
    ) -> None:
        statement = select(UserConfidenceScore).where(UserConfidenceScore.user_id == user_id)
        existing_scores = self.db.exec(statement).all()
        # Clear existing confidence scores
        for confidence_score in existing_scores:
            self.db.delete(confidence_score)
        self.db.commit()
        # Add new confidence scores
        for confidence_score in confidence_scores:
            new_confidence_score = UserConfidenceScore(
                user_id=user_id,
                confidence_area=confidence_score.confidence_area,
                score=confidence_score.score,
            )
            self.db.add(new_confidence_score)

        self.db.commit()

    def replace_user_profile(
        self, user: UserProfile, data: UserProfileReplace
    ) -> UserProfileExtendedRead:
        # Update UserProfile fields
        user.full_name = data.full_name
        user.experience = data.experience
        user.preferred_language_code = data.preferred_language_code
        user.preferred_learning_style = data.preferred_learning_style
        user.store_conversations = data.store_conversations
        user.professional_role = data.professional_role

        # Only admins can change the account role
        if data.account_role and user.account_role == 'admin':
            user.account_role = data.account_role
        elif data.account_role:
            raise HTTPException(
                status_code=403,
                detail='Only admins can change the account role.',
            )

        self.db.add(user)

        # Update goals
        if not data.goals:
            raise HTTPException(status_code=400, detail='Goals cannot be empty')
        self._update_goals(user.id, data.goals)

        # Update confidence scores
        if not data.confidence_scores:
            raise HTTPException(status_code=400, detail='Confidence scores cannot be empty')
        self._update_confidence_scores(user.id, data.confidence_scores)

        self.db.refresh(user)

        return self._get_detailed_user_profile_response(user)

    def update_user_profile(
        self, user: UserProfile, data: UserProfileUpdate
    ) -> UserProfileExtendedRead:
        # Update UserProfile fields if provided
        if data.experience is not None:
            user.experience = data.experience
        if data.preferred_language_code is not None:
            user.preferred_language_code = data.preferred_language_code
        if data.preferred_learning_style is not None:
            user.preferred_learning_style = data.preferred_learning_style
        if data.store_conversations is not None:
            user.store_conversations = data.store_conversations
        if data.professional_role is not None:
            user.professional_role = data.professional_role

        if data.account_role is not None:
            if user.account_role == 'admin':
                user.account_role = data.account_role
            else:
                raise HTTPException(
                    status_code=403,
                    detail='Only admins can change the account role.',
                )

        self.db.add(user)
        # Update goals if provided
        if data.goals is not None:
            self._update_goals(user.id, data.goals)

        # Update confidence scores if provided
        if data.confidence_scores is not None:
            self._update_confidence_scores(user.id, data.confidence_scores)

        self.db.commit()
        self.db.refresh(user)

        return self._get_detailed_user_profile_response(user)

    def _delete_user(self, user_id: UUID) -> dict:
        user = self.db.get(UserProfile, user_id)  # type: ignore
        if not user:
            raise HTTPException(status_code=404, detail='User profile not found')
        self.db.delete(user)
        self.db.commit()
        return {'message': 'User profile deleted successfully'}
