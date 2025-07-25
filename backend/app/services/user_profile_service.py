import logging
from math import ceil
from typing import Union
from uuid import UUID

from fastapi import HTTPException, status
from pydantic import ValidationError
from sqlmodel import Session as DBSession
from sqlmodel import col, select
from supabase import AuthError

from app.database import get_supabase_client
from app.enums.account_role import AccountRole
from app.enums.goal import Goal
from app.models.app_config import AppConfig
from app.models.user_confidence_score import UserConfidenceScore
from app.models.user_goal import UserGoal
from app.models.user_profile import UserProfile
from app.schemas.user_confidence_score import ConfidenceScoreRead
from app.schemas.user_profile import (
    PaginatedUserRead,
    ScenarioAdvice,
    UserEmailRead,
    UserProfileExtendedRead,
    UserProfileRead,
    UserProfileReplace,
    UserProfileUpdate,
    UserStatistics,
)
from app.services.conversation_scenario_service import ConversationScenarioService


class UserService:
    def __init__(self, db: DBSession) -> None:
        self.db = db

    def _get_detailed_user_profile_response(self, user: UserProfile) -> UserProfileExtendedRead:
        daily_session_limit = self.db.exec(
            select(AppConfig.value).where(AppConfig.key == 'dailyUserSessionLimit')
        ).first()
        daily_session_limit = int(daily_session_limit) if daily_session_limit is not None else 0

        # If session limit is not configured, assume limit is hit (safety feature)
        if daily_session_limit == 0:
            num_remaining_daily_sessions = 0
        else:
            num_remaining_daily_sessions = max(0, daily_session_limit - user.sessions_created_today)

        try:
            scenario_advice = ScenarioAdvice.model_validate(user.scenario_advice)
        except ValidationError:
            scenario_advice = {}

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
            sessions_created_today=user.sessions_created_today,
            last_session_date=user.last_session_date,
            num_remaining_daily_sessions=num_remaining_daily_sessions,
            scenario_advice=scenario_advice,
        )

    def _get_user_profile_response(self, user: UserProfile) -> UserProfileRead:
        daily_session_limit = self.db.exec(
            select(AppConfig.value).where(AppConfig.key == 'dailyUserSessionLimit')
        ).first()
        daily_session_limit = int(daily_session_limit) if daily_session_limit is not None else 0

        # If session limit is not configured, assume limit is hit (safety feature)
        if daily_session_limit == 0:
            num_remaining_daily_sessions = 0
        else:
            num_remaining_daily_sessions = max(0, daily_session_limit - user.sessions_created_today)

        try:
            scenario_advice = ScenarioAdvice.model_validate(user.scenario_advice)
        except ValidationError:
            scenario_advice = {}

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
            sessions_created_today=user.sessions_created_today,
            last_session_date=user.last_session_date,
            num_remaining_daily_sessions=num_remaining_daily_sessions,
            scenario_advice=scenario_advice,
        )

    def get_user_profiles(
        self, page: int = 1, page_size: int = 10, email_substring: str | None = None
    ) -> PaginatedUserRead:
        statement = select(UserProfile)
        if email_substring:
            statement = statement.where(col(UserProfile.email).like(f'%{email_substring}%'))

        statement = statement.order_by(col(UserProfile.updated_at).desc())

        all_users = self.db.exec(statement).all()
        total_users = len(all_users)
        if total_users == 0:
            return PaginatedUserRead(
                page=page,
                limit=page_size,
                total_pages=1,
                total_users=0,
                users=[],
            )

        total_pages = ceil(total_users / page_size)
        if page < 1 or page > total_pages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid page number.',
            )

        users = all_users[(page - 1) * page_size : (page) * page_size]
        user_list = [UserEmailRead(user_id=user.id, email=user.email) for user in users]

        return PaginatedUserRead(
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

    def get_user_statistics(self, user_id: UUID) -> UserStatistics:
        user = self.db.get(UserProfile, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User profile not found.',
            )

        daily_session_limit = self.db.exec(
            select(AppConfig.value).where(AppConfig.key == 'dailyUserSessionLimit')
        ).first()
        daily_session_limit = int(daily_session_limit) if daily_session_limit is not None else 0

        # If session limit is not configured, assume limit is hit (safety feature)
        if daily_session_limit == 0:
            num_remaining_daily_sessions = 0
        else:
            num_remaining_daily_sessions = max(0, daily_session_limit - user.sessions_created_today)
        return UserStatistics(
            total_sessions=user.total_sessions,
            training_time=user.training_time,
            current_streak_days=user.current_streak_days,
            score_sum=user.score_sum,
            goals_achieved=user.goals_achieved,
            daily_session_limit=daily_session_limit,
            num_remaining_daily_sessions=num_remaining_daily_sessions,
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
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Only admins can change the account role.',
            )

        self.db.add(user)

        # Update goals
        if not data.goals:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Goals cannot be empty'
            )
        self._update_goals(user.id, data.goals)

        # Update confidence scores
        if not data.confidence_scores:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail='Confidence scores cannot be empty'
            )
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
                    status_code=status.HTTP_403_FORBIDDEN,
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
        user = self.db.get(UserProfile, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail='User profile not found'
            )

        conversation_service = ConversationScenarioService(self.db)
        try:
            conversation_service.clear_all_conversation_scenarios(user)
        except Exception as e:
            logging.error(f'Failed to clear conversation scenarios for user {user_id}: {e}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to clear conversation scenarios',
            ) from e

        try:
            self.db.delete(user)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Failed to delete user'
            ) from e

        try:
            self._delete_supabase_user(user_id)
        except Exception:
            logging.warning(
                f'Deleted user {user_id} from user_profiles table but not from supabase auth table'
                '. Admin action required!'
            )

        return {'message': 'User profile deleted successfully'}

    def _delete_supabase_user(self, user_id: UUID) -> None:
        try:
            supabase = get_supabase_client()
            supabase.auth.admin.delete_user(str(user_id))
        except AuthError as e:
            if e.code != 'user_not_found':
                raise e
        except Exception as e:
            raise e

    def delete_user_profile(self, user_profile: UserProfile, delete_user_id: UUID | None) -> dict:
        if delete_user_id and user_profile.account_role == AccountRole.admin:
            # Check if the admin is trying to delete another admin that is not himself
            if delete_user_id != user_profile.id:
                delete_user = self.db.get(UserProfile, delete_user_id)
                if delete_user and delete_user.account_role == AccountRole.admin:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail='Admin cannot delete another admin ',
                    )

            return self._delete_user(delete_user_id)
        elif delete_user_id and delete_user_id != user_profile.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Admin access required to delete other users',
            )
        else:
            return self._delete_user(user_profile.id)
