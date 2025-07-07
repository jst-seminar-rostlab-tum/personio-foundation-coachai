"""add custom claims

Revision ID: 148e20e323fa
Revises: b2117ff73279
Create Date: 2025-07-07 23:00:56.839769

"""

from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '148e20e323fa'
down_revision: Union[str, None] = 'b2117ff73279'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute("""
        -- Create the auth hook function
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
            select account_role into user_role from public.userprofile where id = (event->>'user_id')::uuid;

            claims := event->'claims';

            if user_role is not null then
                -- Set the claim
                claims := jsonb_set(claims, '{account_role}', to_jsonb(user_role));
            else
                claims := jsonb_set(claims, '{account_role}', 'null');
            end if;

            -- Update the 'claims' object in the original event
            event := jsonb_set(event, '{claims}', claims);

            -- Return the modified or original event
            return event;
        end;
        $$;

        grant usage on schema public to supabase_auth_admin;

        grant execute
        on function public.custom_access_token_hook
        to supabase_auth_admin;

        revoke execute
        on function public.custom_access_token_hook
        from authenticated, anon, public;

        grant all
        on table public.userprofile
        to supabase_auth_admin;

        revoke all
        on table public.userprofile
        from authenticated, anon, public;

        create policy "Allow auth admin to read user roles" ON public.userprofile
        as permissive for select
        to supabase_auth_admin
        using (true)
    """)  # noqa: E501


def downgrade() -> None:
    """Downgrade schema."""

    op.execute("""
        REVOKE ALL ON TABLE public.userprofile FROM supabase_auth_admin;
        REVOKE USAGE ON SCHEMA public FROM supabase_auth_admin;
        REVOKE EXECUTE ON FUNCTION public.custom_access_token_hook FROM supabase_auth_admin;
        REVOKE ALL ON FUNCTION public.custom_access_token_hook FROM authenticated, anon, public;
        REVOKE ALL ON TABLE public.userprofile FROM authenticated, anon, public;
        REVOKE USAGE ON SCHEMA public FROM authenticated, anon, public;
        REVOKE ALL ON SCHEMA public FROM authenticated, anon, public;
        DROP POLICY IF EXISTS "Allow auth admin to read user roles" ON public.userprofile;
        DROP FUNCTION IF EXISTS public.custom_access_token_hook(event jsonb);
    """)
