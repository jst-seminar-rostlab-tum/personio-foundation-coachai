"""delete unused fields in conversation category

Revision ID: d3ba5c881bc7
Revises: 2ec9cbc6c3f2
Create Date: 2025-06-30 23:29:15.251361

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd3ba5c881bc7'
down_revision: Union[str, None] = '2ec9cbc6c3f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('conversationcategory', 'system_prompt')
    op.drop_column('conversationcategory', 'ai_setup')
    op.drop_column('conversationcategory', 'default_goal')
    op.drop_column('conversationcategory', 'default_other_party')
    op.drop_column('conversationcategory', 'default_context')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        'conversationcategory',
        sa.Column('default_context', sa.VARCHAR(), nullable=True),
    )
    op.add_column(
        'conversationcategory',
        sa.Column('default_other_party', sa.VARCHAR(), nullable=True),
    )
    op.add_column(
        'conversationcategory',
        sa.Column('default_goal', sa.VARCHAR(), nullable=True),
    )
    op.add_column(
        'conversationcategory',
        sa.Column('ai_setup', postgresql.JSON(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        'conversationcategory',
        sa.Column('system_prompt', sa.VARCHAR(), nullable=True),
    )
