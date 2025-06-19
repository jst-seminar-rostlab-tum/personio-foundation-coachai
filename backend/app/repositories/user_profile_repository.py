from uuid import UUID

from sqlmodel import Session as DBSession
from sqlmodel import select

from app.models.user_confidence_score import ConfidenceScoreRead, UserConfidenceScore
from app.models.user_goal import Goal, UserGoal
from app.models.user_profile import UserProfile, UserProfileReplace, UserProfileUpdate


class UserProfileRepository:
    def __init__(self, db: DBSession) -> None:
        self.db: DBSession = db

    def get_all(self) -> list[UserProfile]:
        return list(self.db.exec(select(UserProfile)).all())

    def get(self, user_id: UUID) -> UserProfile | None:
        return self.db.get(UserProfile, user_id)

    def replace(self, user: UserProfile, data: UserProfileReplace) -> UserProfile:
        for key, value in data.model_dump().items():
            setattr(user, key, value)
        self._replace_related(user, data)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: UserProfile, data: UserProfileUpdate) -> UserProfile:
        for key, value in data.model_dump(exclude_unset=True).items():
            if key in ['goals', 'confidence_scores']:
                continue
            setattr(user, key, value)

        if data.goals is not None:
            self._replace_goals(user, data.goals)
        if data.confidence_scores is not None:
            self._replace_confidence_scores(user, data.confidence_scores)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: UUID) -> None:
        user = self.get(user_id)
        self.db.delete(user)
        self.db.commit()

    def _replace_related(self, user: UserProfile, data: UserProfileReplace) -> None:
        self._replace_goals(user, data.goals)
        self._replace_confidence_scores(user, data.confidence_scores)

    def _replace_goals(self, user: UserProfile, goals: list[Goal]) -> None:
        for ug in user.user_goals:
            self.db.delete(ug)
        self.db.commit()
        for goal in goals:
            self.db.add(UserGoal(user_id=user.id, goal=Goal(goal)))

    def _replace_confidence_scores(
        self, user: UserProfile, scores: list[ConfidenceScoreRead]
    ) -> None:
        for cs in user.user_confidence_scores:
            self.db.delete(cs)
        self.db.commit()
        for cs in scores:
            self.db.add(UserConfidenceScore(user_id=user.id, **cs.model_dump()))
