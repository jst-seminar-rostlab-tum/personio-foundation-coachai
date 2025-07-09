"""Add pg_graphql and vector (CI-safe)

Revision ID: e02cc4b53875
Revises: a1e923719659
Create Date: 2025-07-09 19:57:37.813168
"""

from collections.abc import Sequence
from typing import Union

from alembic import op

# Revision identifiers, used by Alembic.
revision: str = 'e02cc4b53875'
down_revision: Union[str, None] = 'a1e923719659'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_roles WHERE rolname = 'supabase_admin'
            ) THEN
                CREATE ROLE supabase_admin SUPERUSER;
            END IF;
        END
        $$;
        """
    )
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_graphql;')
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')


def downgrade() -> None:
    """Downgrade schema.

    This revision only **ensures** that the `pg_graphql` and `vector`
    extensions are present. Earlier revisions still depend on them, so
    we make the downgrade a no‑op. The initial migration (`ccbf2a5fb6a6`)
    will drop the extensions automatically once all dependent objects
    are gone.
    """

    pass
