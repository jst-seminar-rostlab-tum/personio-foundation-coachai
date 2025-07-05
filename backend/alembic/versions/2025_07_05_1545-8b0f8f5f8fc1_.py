"""empty message

Revision ID: 8b0f8f5f8fc1
Revises: 24eaf11003f7, a93e502a5d3a
Create Date: 2025-07-05 15:45:46.089730

"""

from collections.abc import Sequence
from typing import Union

# revision identifiers, used by Alembic.
revision: str = '8b0f8f5f8fc1'
down_revision: Union[str, None] = ('24eaf11003f7', 'a93e502a5d3a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
