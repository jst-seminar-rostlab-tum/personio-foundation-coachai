"""merge heads

Revision ID: 96c80a88a4d6
Revises: effa95c38794, d3ba5c881bc7
Create Date: 2025-07-02 17:49:58.172321

"""

from collections.abc import Sequence
from typing import Union

# revision identifiers, used by Alembic.
revision: str = '96c80a88a4d6'
down_revision: Union[str, None] = ('effa95c38794', 'd3ba5c881bc7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
