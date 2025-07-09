"""Add pg_graphql and vector (CI-safe)

Revision ID: e02cc4b53875
Revises: a1e923719659
Create Date: 2025-07-09 19:57:37.813168
"""

from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e02cc4b53875'
down_revision: Union[str, None] = 'a1e923719659'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ──────────────────────────────────────────────────────────
    # 1. Ensure the Supabase super-role exists (no-op on prod)
    # ──────────────────────────────────────────────────────────
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

    # ──────────────────────────────────────────────────────────
    # 2. Install required extensions
    # ──────────────────────────────────────────────────────────
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_graphql;')
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')  # needs supabase_admin


def downgrade() -> None:
    """Downgrade schema."""

    # Drop extensions in reverse order of creation.
    # We intentionally leave the supabase_admin role in place:
    #   – it may be used by other extensions or later migrations
    op.execute('DROP EXTENSION IF EXISTS vector;')
    op.execute('DROP EXTENSION IF EXISTS pg_graphql;')
