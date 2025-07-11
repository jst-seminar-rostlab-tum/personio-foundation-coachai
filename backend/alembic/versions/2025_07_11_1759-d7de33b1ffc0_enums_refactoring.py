"""enums refactoring

Revision ID: d7de33b1ffc0
Revises: 3dfcba1ec486
Create Date: 2025-07-11 17:59:16.821357

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd7de33b1ffc0'
down_revision: Union[str, None] = '3dfcba1ec486'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create new ENUM types
    feedback_status_enum = sa.Enum('pending', 'completed', 'failed', name='feedbackstatus')
    speaker_type_enum = sa.Enum('user', 'assistant', name='speakertype')

    feedback_status_enum.create(op.get_bind())
    speaker_type_enum.create(op.get_bind())

    # Alter columns using explicit cast
    op.alter_column(
        'sessionfeedback',
        'status',
        existing_type=postgresql.ENUM('pending', 'completed', 'failed', name='feedbackstatusenum'),
        type_=feedback_status_enum,
        existing_nullable=False,
        postgresql_using='status::text::feedbackstatus',
    )
    op.alter_column(
        'sessionturn',
        'speaker',
        existing_type=postgresql.ENUM('user', 'assistant', name='speakerenum'),
        type_=speaker_type_enum,
        existing_nullable=False,
        postgresql_using='speaker::text::speakertype',
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Revert columns to old ENUMs
    op.alter_column(
        'sessionturn',
        'speaker',
        existing_type=sa.Enum('user', 'assistant', name='speakertype'),
        type_=postgresql.ENUM('user', 'assistant', name='speakerenum'),
        existing_nullable=False,
    )
    op.alter_column(
        'sessionfeedback',
        'status',
        existing_type=sa.Enum('pending', 'completed', 'failed', name='feedbackstatus'),
        type_=postgresql.ENUM('pending', 'completed', 'failed', name='feedbackstatusenum'),
        existing_nullable=False,
    )

    # Drop the new ENUM types
    speaker_type_enum = sa.Enum('user', 'assistant', name='speakertype')
    feedback_status_enum = sa.Enum('pending', 'completed', 'failed', name='feedbackstatus')
    speaker_type_enum.drop(op.get_bind())
    feedback_status_enum.drop(op.get_bind())
    # ### end Alembic commands ###
