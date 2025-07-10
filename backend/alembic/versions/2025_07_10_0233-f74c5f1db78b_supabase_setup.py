"""Supabase setup

Revision ID: f74c5f1db78b
Revises: 79cce3e613d2
Create Date: 2025-07-10 02:33:02.845299
"""

from collections.abc import Sequence
from typing import Union

from alembic import op

# ────────────────────────────────────────────────────────────────────────────────
revision: str = 'f74c5f1db78b'
down_revision: Union[str, None] = '79cce3e613d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
# ────────────────────────────────────────────────────────────────────────────────


def upgrade() -> None:  # noqa: D401
    """Add Supabase roles, extensions and JWT claim hook."""

    # --------------------------------------------------------------------- roles
    op.execute(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (
              SELECT 1 FROM pg_roles WHERE rolname = 'supabase_admin'
          ) THEN
            CREATE ROLE supabase_admin SUPERUSER;
          END IF;
        END;
        $$;
        """
    )

    # --------------------------------------------------------------- extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_graphql;')
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')

    # ---------------------------------------------------- custom claims PL/pgSQL
    op.execute(
        """
        ----------------------------------------------------------------------------
        -- Function: public.custom_access_token_hook(event jsonb)
        -- Purpose : Injects `account_role` into JWT access tokens issued by Supabase
        ----------------------------------------------------------------------------
        CREATE OR REPLACE FUNCTION public.custom_access_token_hook(event jsonb)
        RETURNS jsonb
        LANGUAGE plpgsql
        STABLE
        AS $fn$
        DECLARE
          claims    jsonb;
          user_role public.accountrole;
        BEGIN
          SELECT account_role
            INTO user_role
            FROM public.userprofile
           WHERE id = (event->>'user_id')::uuid;

          claims := event->'claims';

          IF user_role IS NOT NULL THEN
            claims := jsonb_set(claims, '{account_role}', to_jsonb(user_role));
          ELSE
            claims := jsonb_set(claims, '{account_role}', 'null');
          END IF;

          event := jsonb_set(event, '{claims}', claims);
          RETURN event;
        END;
        $fn$;

        ----------------------------------------------------------------------------
        -- Privileges / policies
        ----------------------------------------------------------------------------
        GRANT USAGE   ON SCHEMA  public TO supabase_auth_admin;
        GRANT EXECUTE ON FUNCTION public.custom_access_token_hook
          TO supabase_auth_admin;

        DO $do$
        BEGIN
          -- Only revoke when the roles exist (plain Postgres in CI does not have them)
          IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
            REVOKE EXECUTE ON FUNCTION public.custom_access_token_hook
              FROM authenticated;
            REVOKE ALL ON TABLE public.userprofile FROM authenticated;
          END IF;

          IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
            REVOKE EXECUTE ON FUNCTION public.custom_access_token_hook FROM anon;
            REVOKE ALL ON TABLE public.userprofile FROM anon;
          END IF;

          -- Always clean up PUBLIC
          REVOKE ALL ON TABLE public.userprofile FROM PUBLIC;
        END;
        $do$;

        GRANT ALL ON TABLE public.userprofile TO supabase_auth_admin;

        -- (Re-)create policy tied to the auth role
        DROP POLICY IF EXISTS "Allow auth admin to read user roles"
          ON public.userprofile;

        CREATE POLICY "Allow auth admin to read user roles"
          ON public.userprofile
          AS PERMISSIVE FOR SELECT
          TO supabase_auth_admin
          USING (true);
        """
    )


def downgrade() -> None:  # noqa: D401
    """Remove everything introduced in :func:`upgrade`."""

    op.execute(
        """
        DO $do$
        BEGIN
          -- Revoke grants created in upgrade()
          IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'supabase_auth_admin') THEN
            REVOKE ALL    ON TABLE public.userprofile FROM supabase_auth_admin;
            REVOKE EXECUTE ON FUNCTION public.custom_access_token_hook
              FROM supabase_auth_admin;
          END IF;

          IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
            REVOKE ALL    ON TABLE public.userprofile FROM authenticated;
            REVOKE EXECUTE ON FUNCTION public.custom_access_token_hook
              FROM authenticated;
          END IF;

          IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
            REVOKE ALL    ON TABLE public.userprofile FROM anon;
            REVOKE EXECUTE ON FUNCTION public.custom_access_token_hook FROM anon;
          END IF;

          REVOKE ALL ON TABLE public.userprofile FROM PUBLIC;
        END;
        $do$;

        DROP POLICY IF EXISTS "Allow auth admin to read user roles"
          ON public.userprofile;

        DROP FUNCTION IF EXISTS public.custom_access_token_hook(event jsonb);
        -- pg_graphql and vector stay; older revisions may still rely on them.
        """
    )
