"""empty message

Revision ID: 52523a841222
Revises: ad0abf669301, 54d72c3444d6
Create Date: 2025-06-29 17:54:05.932315

"""

from collections.abc import Sequence
from typing import Union

# revision identifiers, used by Alembic.
revision: str = '52523a841222'
down_revision: Union[str, None] = ('ad0abf669301', '54d72c3444d6')  # type: ignore
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
