"""change overall_score to float in sessionfeedback

Revision ID: effa95c38794
Revises: 7968f3435129
Create Date: 2025-06-30 21:33:40.170606

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'effa95c38794'
down_revision: Union[str, None] = '7968f3435129'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Change overall_score to float
    op.alter_column(
        'sessionfeedback', 'overall_score', type_=sa.Float(), existing_type=sa.Integer()
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Change overall_score to integer
    op.alter_column(
        'sessionfeedback', 'overall_score', type_=sa.Integer(), existing_type=sa.Float()
    )
