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

    feedback_status = sa.Enum('pending', 'completed', 'failed', name='feedbackstatus')
    speaker_type = sa.Enum('user', 'assistant', name='speakertype')

    feedback_status.create(op.get_bind(), checkfirst=True)
    speaker_type.create(op.get_bind(), checkfirst=True)

    op.alter_column(
        'sessionfeedback',
        'status',
        existing_type=postgresql.ENUM('pending', 'completed', 'failed', name='feedbackstatusenum'),
        type_=feedback_status,
        existing_nullable=False,
        postgresql_using='status::text::feedbackstatus',
    )

    op.alter_column(
        'sessionturn',
        'speaker',
        existing_type=postgresql.ENUM('user', 'assistant', name='speakerenum'),
        type_=speaker_type,
        existing_nullable=False,
        postgresql_using='speaker::text::speakertype',
    )
    op.execute('DROP TYPE IF EXISTS feedbackstatusenum')
    op.execute('DROP TYPE IF EXISTS speakerenum')


def downgrade() -> None:
    """Downgrade schema."""

    bind = op.get_bind()
    old_feedback_status = postgresql.ENUM(
        'pending', 'completed', 'failed', name='feedbackstatusenum'
    )
    old_speaker_enum = postgresql.ENUM('user', 'assistant', name='speakerenum')

    old_feedback_status.create(bind, checkfirst=True)
    old_speaker_enum.create(bind, checkfirst=True)

    op.alter_column(
        'sessionfeedback',
        'status',
        existing_type=sa.Enum('pending', 'completed', 'failed', name='feedbackstatus'),
        type_=old_feedback_status,
        existing_nullable=False,
        postgresql_using='status::text::feedbackstatusenum',
    )

    op.alter_column(
        'sessionturn',
        'speaker',
        existing_type=sa.Enum('user', 'assistant', name='speakertype'),
        type_=old_speaker_enum,
        existing_nullable=False,
        postgresql_using='speaker::text::speakerenum',
    )

    feedback_status = sa.Enum('pending', 'completed', 'failed', name='feedbackstatus')
    speaker_type = sa.Enum('user', 'assistant', name='speakertype')

    feedback_status.drop(bind, checkfirst=True)
    speaker_type.drop(bind, checkfirst=True)
