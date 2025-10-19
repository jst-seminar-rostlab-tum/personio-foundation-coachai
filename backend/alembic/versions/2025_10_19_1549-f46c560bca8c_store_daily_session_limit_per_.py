"""store daily session limit per individual user

Revision ID: f46c560bca8c
Revises: ab7ebf70f8b9
Create Date: 2025-10-19 15:49:20.070792

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'f46c560bca8c'
down_revision: Union[str, None] = 'ab7ebf70f8b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('userprofile', sa.Column('daily_session_limit', sa.Integer(), nullable=True))
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE appconfig
            SET key = 'defaultDailyUserSessionLimit'
            WHERE key = 'dailyUserSessionLimit';
        """)
    )


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(
        sa.text("""
            UPDATE appconfig
            SET key = 'dailyUserSessionLimit'
            WHERE key = 'defaultDailyUserSessionLimit';
        """)
    )
    op.drop_column('userprofile', 'daily_session_limit')
