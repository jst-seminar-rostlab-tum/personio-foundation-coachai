"""add allow_admin_access to review

Revision ID: 92a5ad9d1a57
Revises: 0a10f61dc9c7
Create Date: 2025-06-25 00:45:14.059383
"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '92a5ad9d1a57'
down_revision: Union[str, None] = '0a10f61dc9c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add column as NOT NULL with server-side default 'false'
    op.add_column(
        'review',
        sa.Column(
            'allow_admin_access', sa.Boolean(), nullable=False, server_default=sa.text('false')
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('review', 'allow_admin_access')
