from enum import Enum as PyEnum


class ProfessionalRole(str, PyEnum):
    hr_professional = 'hr_professional'
    team_leader = 'team_leader'
    executive = 'executive'
    other = 'other'
