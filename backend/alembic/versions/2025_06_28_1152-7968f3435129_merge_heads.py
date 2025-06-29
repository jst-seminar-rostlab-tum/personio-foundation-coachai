"""merge heads

Revision ID: 7968f3435129
Revises: 54d72c3444d6, a131a5542baa
Create Date: 2025-06-28 11:52:27.485178

"""

from collections.abc import Sequence
from typing import Union

# revision identifiers, used by Alembic.
revision: str = '7968f3435129'
down_revision: Union[str, None] = ('54d72c3444d6', 'a131a5542baa')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
