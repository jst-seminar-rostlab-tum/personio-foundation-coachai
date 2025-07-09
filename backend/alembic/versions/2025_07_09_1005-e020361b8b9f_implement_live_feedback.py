"""implement_live_feedback

Revision ID: e020361b8b9f
Revises: b2117ff73279
Create Date: 2025-07-09 10:05:22.995775

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e020361b8b9f'
down_revision: Union[str, None] = 'b2117ff73279'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create live_feedback table."""
    op.create_table(
        'livefeedback',
        sa.Column(
            'id',
            sa.UUID,
            primary_key=True,
            nullable=False,
            server_default=sa.text('gen_random_uuid()'),
        ),
        sa.Column(
            'session_id',
            sa.UUID,
            sa.ForeignKey('session.id'),
            nullable=False,
        ),
        sa.Column('heading', sa.String(length=255), nullable=False),
        sa.Column('feedback_text', sa.String(length=255), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP'),
        ),
    )


def downgrade() -> None:
    """Drop live_feedback table."""
    op.drop_table('livefeedback')
