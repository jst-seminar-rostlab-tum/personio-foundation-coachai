"""replace average_score with score_sum in user_profile and admin_dashboard_stats

Revision ID: a131a5542baa
Revises: 0a10f61dc9c7
Create Date: 2025-06-27 16:32:25.473457

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a131a5542baa'
down_revision: Union[str, None] = '0a10f61dc9c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # user_profile
    with op.batch_alter_table('userprofile') as batch_op:
        batch_op.drop_column('average_score')
        batch_op.add_column(sa.Column('score_sum', sa.Float(), nullable=False, server_default='0'))
    # admin_dashboard_stats
    with op.batch_alter_table('admindashboardstats') as batch_op:
        batch_op.drop_column('average_score')
        batch_op.add_column(sa.Column('score_sum', sa.Float(), nullable=False, server_default='0'))


def downgrade() -> None:
    """Downgrade schema."""
    # user_profile
    with op.batch_alter_table('userprofile') as batch_op:
        batch_op.add_column(
            sa.Column('average_score', sa.Integer(), nullable=False, server_default='0')
        )
        batch_op.drop_column('score_sum')
    # admin_dashboard_stats
    with op.batch_alter_table('admindashboardstats') as batch_op:
        batch_op.add_column(
            sa.Column('average_score', sa.Integer(), nullable=False, server_default='82')
        )
        batch_op.drop_column('score_sum')
