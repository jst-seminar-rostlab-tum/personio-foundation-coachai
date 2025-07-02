"""empty message

Revision ID: d74599307cf1
Revises: d2dab6bb11ac, d3ba5c881bc7
Create Date: 2025-07-02 14:21:07.502234

"""

from collections.abc import Sequence
from typing import Union

# revision identifiers, used by Alembic.
revision: str = 'd74599307cf1'
down_revision: Union[str, None] = ('d2dab6bb11ac', 'd3ba5c881bc7')  # type: ignore
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
