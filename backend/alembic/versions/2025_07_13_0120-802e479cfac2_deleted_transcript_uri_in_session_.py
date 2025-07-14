"""deleted transcript_uri in session_feedback

Revision ID: 802e479cfac2
Revises: d7de33b1ffc0
Create Date: 2025-07-13 01:20:39.421001

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '802e479cfac2'
down_revision: Union[str, None] = '47073b70baec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column('sessionfeedback', 'transcript_uri')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        'sessionfeedback',
        sa.Column('transcript_uri', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.execute("UPDATE sessionfeedback SET transcript_uri = ''")
    op.alter_column('sessionfeedback', 'transcript_uri', nullable=False)
    # ### end Alembic commands ###
