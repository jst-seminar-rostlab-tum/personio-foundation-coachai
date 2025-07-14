"""merge heads

Revision ID: a93e502a5d3a
Revises: 96c80a88a4d6, 7718ddcf9e37
Create Date: 2025-07-03 21:06:07.422596

"""

from collections.abc import Sequence
from typing import Union

# revision identifiers, used by Alembic.
revision: str = 'a93e502a5d3a'
down_revision: Union[str, None] = ('96c80a88a4d6', '7718ddcf9e37')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
