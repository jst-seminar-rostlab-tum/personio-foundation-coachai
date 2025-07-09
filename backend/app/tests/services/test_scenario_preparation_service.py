"""Add pg_graphql, vector extensions and custom claims (CI‑safe)

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


def upgrade() -> None:  # noqa: D401
    """Upgrade schema.

    * Ensures critical Supabase roles exist (`supabase_admin`, `supabase_auth_admin`).
    * Installs the `pg_graphql` and `vector` extensions if missing.
    * Adds the `custom_access_token_hook` function and wires up all required
      privileges and a read‑only policy for the Supabase Auth service.
    """

    # ---------------------------------------------------------
    # Core roles / extensions (idempotent)
    # ---------------------------------------------------------
    op.execute(
        """
        DO $$
        BEGIN
            -- Create the Supabase core roles if they are absent.
            IF NOT EXISTS (
                SELECT 1 FROM pg_roles WHERE rolname = 'supabase_admin'
            ) THEN
                CREATE ROLE supabase_admin SUPERUSER;
            END IF;

            IF NOT EXISTS (
                SELECT 1 FROM pg_roles WHERE rolname = 'supabase_auth_admin'
            ) THEN
                -- No special attributes — just a service role.
                CREATE ROLE supabase_auth_admin;
            END IF;
        END;
        $$;
        """
    )

    # Required PostgreSQL extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_graphql;')
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')

    # ---------------------------------------------------------
    # Custom JWT claim hook + security plumbing
    # ---------------------------------------------------------
    op.execute(
        """
        -- ------------------------------------------------------------------
        -- Function: public.custom_access_token_hook(event jsonb)
        -- Purpose : Adds `account_role` claim to JWT access tokens issued by
        --            Supabase Auth.
        -- ------------------------------------------------------------------
        CREATE OR REPLACE FUNCTION public.custom_access_token_hook(event jsonb)
        RETURNS jsonb
        LANGUAGE plpgsql
        STABLE AS $$
        DECLARE
            claims     jsonb;
            user_role  public.accountrole;
        BEGIN
            -- Lookup user's role (nullable)
            SELECT account_role
              INTO user_role
              FROM public.userprofile
             WHERE id = (event->>'user_id')::uuid;

            -- Copy existing set of claims
            claims := event->'claims';

            IF user_role IS NOT NULL THEN
                claims := jsonb_set(claims, '{account_role}', to_jsonb(user_role));
            ELSE
                claims := jsonb_set(claims, '{account_role}', 'null');
            END IF;

            -- Write back mutated claims
            event := jsonb_set(event, '{claims}', claims);
            RETURN event;
        END;
        $$;

        -- Allow only the Supabase Auth service to use this hook
        GRANT USAGE   ON SCHEMA  public TO supabase_auth_admin;
        GRANT EXECUTE ON FUNCTION public.custom_access_token_hook TO supabase_auth_admin;
        REVOKE EXECUTE ON FUNCTION public.custom_access_token_hook FROM authenticated, anon, public;

        -- Table‑level privileges for the Auth service
        GRANT ALL ON TABLE public.userprofile TO supabase_auth_admin;
        REVOKE ALL ON TABLE public.userprofile FROM authenticated, anon, public;

        -- Ensure policy exists (drop‑then‑create for Postgres <16)
        DROP POLICY IF EXISTS "Allow auth admin to read user roles" ON public.userprofile;
        CREATE POLICY "Allow auth admin to read user roles" ON public.userprofile
            AS PERMISSIVE FOR SELECT
            TO supabase_auth_admin
            USING (true);
        """  # noqa: E501
    )


def downgrade() -> None:  # noqa: D401
    """Downgrade schema.

    * Removes the custom claims hook, grants, and policy.
    * **Does not** drop the `pg_graphql` and `vector` extensions because older
      revisions continue to depend on them; the initial migration will handle
      their removal once no objects reference them.
    """

    op.execute(
        """
        -- Roll back *only* objects introduced by this revision
        REVOKE ALL ON TABLE public.userprofile FROM supabase_auth_admin;
        REVOKE EXECUTE ON FUNCTION public.custom_access_token_hook FROM supabase_auth_admin;
        REVOKE ALL ON TABLE public.userprofile FROM authenticated, anon, public;
        REVOKE ALL ON FUNCTION public.custom_access_token_hook FROM authenticated, anon, public;
        DROP POLICY IF EXISTS "Allow auth admin to read user roles" ON public.userprofile;
        DROP FUNCTION IF EXISTS public.custom_access_token_hook(event jsonb);
        -- NOTE: pg_graphql and vector extensions intentionally left in place.
        """
    )
