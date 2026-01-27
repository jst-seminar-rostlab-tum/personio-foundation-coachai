"""Enum definitions for professional role."""

from enum import Enum as PyEnum


class ProfessionalRole(str, PyEnum):
    """Enum for professional role."""

    hr_professional = 'hr_professional'
    team_leader = 'team_leader'
    executive = 'executive'
    other = 'other'
