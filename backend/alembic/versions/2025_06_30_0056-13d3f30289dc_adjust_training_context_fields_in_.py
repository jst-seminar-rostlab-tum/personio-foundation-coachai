"""adjust training context fields in conversation scenario

Revision ID: 13d3f30289dc
Revises: 54d72c3444d6
Create Date: 2025-06-30 00:56:30.194203

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '13d3f30289dc'
down_revision: Union[str, None] = '54d72c3444d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'conversationscenario',
        sa.Column('persona', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.execute("UPDATE conversationscenario SET persona = ''")
    op.alter_column('conversationscenario', 'persona', nullable=False)

    op.add_column(
        'conversationscenario',
        sa.Column('situational_facts', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    )
    op.execute("UPDATE conversationscenario SET situational_facts = ''")
    op.alter_column('conversationscenario', 'situational_facts', nullable=False)

    op.drop_column('conversationscenario', 'complexity')
    op.drop_column('conversationscenario', 'other_party')
    op.drop_column('conversationscenario', 'context')
    op.drop_column('conversationscenario', 'goal')
    op.drop_column('conversationscenario', 'tone')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('conversationscenario', 'situational_facts')
    op.drop_column('conversationscenario', 'persona')

    op.add_column(
        'conversationscenario', sa.Column('tone', sa.VARCHAR(), autoincrement=False, nullable=True)
    )

    op.add_column('conversationscenario', sa.Column('goal', sa.VARCHAR(), nullable=True))
    op.execute("UPDATE conversationscenario SET goal = ''")
    op.alter_column('conversationscenario', 'goal', nullable=False)

    op.add_column('conversationscenario', sa.Column('context', sa.VARCHAR(), nullable=True))
    op.execute("UPDATE conversationscenario SET context = ''")
    op.alter_column('conversationscenario', 'context', nullable=False)

    op.add_column('conversationscenario', sa.Column('other_party', sa.VARCHAR(), nullable=True))
    op.execute("UPDATE conversationscenario SET other_party = ''")
    op.alter_column('conversationscenario', 'other_party', nullable=False)

    op.add_column(
        'conversationscenario',
        sa.Column('complexity', sa.VARCHAR(), autoincrement=False, nullable=True),
    )
