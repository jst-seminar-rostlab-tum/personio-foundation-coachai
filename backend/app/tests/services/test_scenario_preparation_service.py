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
    * Adds the `custom_access_token_hook` function, plus conditional grants and
      policy creation so CI can run without the Supabase‑specific roles.
    """

    # ---------------------------------------------------------
    # Core roles / extensions (idempotent)
    # ---------------------------------------------------------
    op.execute(
        """
        -- Create core roles if absent.  These commands *may* silently fail in
        -- CI if the migration user lacks CREATEROLE; that's fine because the
        -- subsequent security plumbing is now fully conditional.
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'supabase_admin') THEN
                CREATE ROLE supabase_admin SUPERUSER;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'supabase_auth_admin') THEN
                CREATE ROLE supabase_auth_admin;
            END IF;
        EXCEPTION WHEN insufficient_privilege THEN
            RAISE NOTICE 'Skipping CREATE ROLE (insufficient privileges)';
        END;
        $$;
        """
    )

    op.execute('CREATE EXTENSION IF NOT EXISTS pg_graphql;')
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')

    # ---------------------------------------------------------
    # Custom JWT claim hook (always created)
    # ---------------------------------------------------------
    op.execute(
        """
        CREATE OR REPLACE FUNCTION public.custom_access_token_hook(event jsonb)
        RETURNS jsonb
        LANGUAGE plpgsql
        STABLE AS $$
        DECLARE
            claims     jsonb;
            user_role  public.accountrole;
        BEGIN
            SELECT account_role INTO user_role
            FROM   public.userprofile
            WHERE  id = (event->>'user_id')::uuid;

            claims := event->'claims';

            IF user_role IS NOT NULL THEN
                claims := jsonb_set(claims, '{account_role}', to_jsonb(user_role));
            ELSE
                claims := jsonb_set(claims, '{account_role}', 'null');
            END IF;

            event := jsonb_set(event, '{claims}', claims);
            RETURN event;
        END;
        $$;
        """
    )

    # ---------------------------------------------------------
    # Conditional security plumbing (only if roles exist)
    # ---------------------------------------------------------
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'supabase_auth_admin') THEN
                EXECUTE 'GRANT USAGE   ON SCHEMA public TO supabase_auth_admin';
                EXECUTE 'GRANT EXECUTE ON FUNCTION public.custom_access_token_hook 
                TO supabase_auth_admin';
                EXECUTE 'GRANT ALL    ON TABLE   public.userprofile TO supabase_auth_admin';

                -- Revoke broad access only if the target roles exist to avoid
                -- errors in vanilla CI databases.
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'authenticated') THEN
                    EXECUTE 'REVOKE EXECUTE ON FUNCTION public.custom_access_token_hook 
                    FROM authenticated';
                    EXECUTE 'REVOKE ALL ON TABLE public.userprofile FROM authenticated';
                END IF;

                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'anon') THEN
                    EXECUTE 'REVOKE EXECUTE ON FUNCTION public.custom_access_token_hook 
                    FROM anon';
                    EXECUTE 'REVOKE ALL ON TABLE public.userprofile FROM anon';
                END IF;

                -- (The implicit "public" role always exists.)
                EXECUTE 'REVOKE EXECUTE ON FUNCTION public.custom_access_token_hook 
                FROM public';
                EXECUTE 'REVOKE ALL ON TABLE public.userprofile FROM public';

                -- (Re‑)create policy tied to the auth role
                EXECUTE 'DROP POLICY IF EXISTS "Allow auth admin to read user roles" 
                ON public.userprofile';
                EXECUTE 'CREATE POLICY "Allow auth admin to read user roles" 
                ON public.userprofile '
                        'AS PERMISSIVE FOR SELECT TO supabase_auth_admin USING (true)';
            ELSE
                RAISE NOTICE 'supabase_auth_admin role missing – skipping grants/policy';
            END IF;
        END;
        $$;
        """
    )


def downgrade() -> None:  # noqa: D401
    """Downgrade schema.

    Removes the custom claims hook, conditional grants, and policy. Extensions
    are intentionally **not** dropped because earlier revisions still depend on
    them; the initial migration handles that once safe.
    """

    op.execute(
        """
        -- Conditional cleanup mirroring the upgrade logic
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'supabase_auth_admin') THEN
                EXECUTE 'REVOKE ALL ON TABLE public.userprofile FROM supabase_auth_admin';
                EXECUTE 'REVOKE EXECUTE ON FUNCTION
                 public.custom_access_token_hook FROM supabase_auth_admin';
            END IF;
        END;
        $$;

        DROP POLICY IF EXISTS "Allow auth admin to read user roles" ON public.userprofile;
        DROP FUNCTION IF EXISTS public.custom_access_token_hook(event jsonb);
        """
    )
