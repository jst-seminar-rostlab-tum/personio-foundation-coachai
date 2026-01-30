"""Enum definitions for goal."""

from enum import Enum as PyEnum


class Goal(str, PyEnum):
    """Enum for goal."""

    giving_constructive_feedback = 'giving_constructive_feedback'
    managing_team_conflicts = 'managing_team_conflicts'
    performance_reviews = 'performance_reviews'
    motivating_team_members = 'motivating_team_members'
    leading_difficult_conversations = 'leading_difficult_conversations'
    communicating_organizational_change = 'communicating_organizational_change'
    develop_emotional_intelligence = 'develop_emotional_intelligence'
    building_inclusive_teams = 'building_inclusive_teams'
    negotiation_skills = 'negotiation_skills'
    coaching_mentoring = 'coaching_mentoring'
