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

    * Ensures the `supabase_admin` superuser role is present.
    * Installs the `pg_graphql` and `vector` extensions if they are missing.
    * Adds the `custom_access_token_hook` for injecting the `account_role` claim
      and wires up all necessary grants and policies to keep the hook secure.
    """

    # Ensure the `supabase_admin` role exists (safe for CI)
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

    # Install required PostgreSQL extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_graphql;')
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')

    # ---------------------------------------------------------------------
    # Custom JWT claim hook: injects `account_role` into the access token.
    # ---------------------------------------------------------------------
    op.execute(
        """
        -- Create the auth hook function (idempotent via CREATE OR REPLACE)
        create or replace function public.custom_access_token_hook(event jsonb)
        returns jsonb
        language plpgsql
        stable
        as $$
        declare
            claims jsonb;
            user_role public.accountrole;
        begin
            -- Fetch the account role from the userprofile table
            select account_role
            into   user_role
            from   public.userprofile
            where  id = (event->>'user_id')::uuid;

            -- Copy existing claims
            claims := event->'claims';

            if user_role is not null then
                -- Inject the claim
                claims := jsonb_set(claims, '{account_role}', to_jsonb(user_role));
            else
                -- Explicitly set to null so callers can trust the key exists
                claims := jsonb_set(claims, '{account_role}', 'null');
            end if;

            -- Write back the updated claims object
            event := jsonb_set(event, '{claims}', claims);

            return event;
        end;
        $$;

        -- Minimal privileges required for the Supabase auth service
        grant usage on schema public to supabase_auth_admin;
        grant execute on function public.custom_access_token_hook to supabase_auth_admin;
        revoke execute on function public.custom_access_token_hook from authenticated, anon, public;

        -- Grant read‑only access on the userprofile table to the auth service
        grant all on table public.userprofile to supabase_auth_admin;
        revoke all on table public.userprofile from authenticated, anon, public;

        -- Policy allowing the auth service to read roles (permissive)
        create policy if not exists "Allow auth admin to read user roles" on public.userprofile
            as permissive for select
            to supabase_auth_admin
            using (true);
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
        -- Roll back the privileges and objects introduced by this revision
        revoke all on table public.userprofile from supabase_auth_admin;
        revoke execute on function public.custom_access_token_hook from supabase_auth_admin;
        revoke all on table public.userprofile from authenticated, anon, public;
        revoke all on function public.custom_access_token_hook from authenticated, anon, public;
        drop policy if exists "Allow auth admin to read user roles" on public.userprofile;
        drop function if exists public.custom_access_token_hook(event jsonb);
        -- NOTE: pg_graphql and vector extensions intentionally left in place.
        """
    )
