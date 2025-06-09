"""initial_db_schema

Revision ID: 92ae6c83f8a8
Revises:
Create Date: 2025-06-06 17:39:11.778173

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
import sqlmodel
from pgvector.sqlalchemy import Vector

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '92ae6c83f8a8'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    op.create_table(
        'appconfig',
        sa.Column('key', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('value', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('type', sa.Enum('int', 'string', 'boolean', name='configtype'), nullable=True),
        sa.PrimaryKeyConstraint('key'),
    )
    op.create_table(
        'confidencearea',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('label', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('min_value', sa.Integer(), nullable=False),
        sa.Column('max_value', sa.Integer(), nullable=False),
        sa.Column('min_label', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('max_label', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'difficultylevel',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('label', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'experience',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('label', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'goal',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('label', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'language',
        sa.Column('code', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint('code'),
    )
    op.create_table(
        'learningstyle',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('label', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'sessionlength',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('label', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'conversationcategory',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('icon_uri', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('system_prompt', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('initial_prompt', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('ai_setup', sa.JSON(), nullable=True),
        sa.Column('default_context', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('default_goal', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('default_other_party', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('is_custom', sa.Boolean(), nullable=False),
        sa.Column('language_code', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['language_code'],
            ['language.code'],
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
    op.create_table(
        'userprofile',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('preferred_language', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('experience_id', sa.Uuid(), nullable=False),
        sa.Column('preferred_learning_style_id', sa.Uuid(), nullable=False),
        sa.Column('preferred_session_length_id', sa.Uuid(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('store_conversations', sa.Boolean(), nullable=False),
        sa.Column('role', sa.Enum('user', 'admin', name='userrole'), nullable=True),
        sa.Column('total_sessions', sa.Integer(), nullable=False),
        sa.Column('training_time', sa.Float(), nullable=False),
        sa.Column('current_streak_days', sa.Integer(), nullable=False),
        sa.Column('average_score', sa.Integer(), nullable=False),
        sa.Column('goals_achieved', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['experience_id'],
            ['experience.id'],
        ),
        sa.ForeignKeyConstraint(
            ['preferred_language'],
            ['language.code'],
        ),
        sa.ForeignKeyConstraint(
            ['preferred_learning_style_id'],
            ['learningstyle.id'],
        ),
        sa.ForeignKeyConstraint(
            ['preferred_session_length_id'],
            ['sessionlength.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'trainingcase',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('category_id', sa.Uuid(), nullable=True),
        sa.Column('custom_category_label', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('context', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('goal', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('other_party', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('difficulty_id', sa.Uuid(), nullable=False),
        sa.Column('tone', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('complexity', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column(
            'status',
            sa.Enum('draft', 'ready', 'archived', name='trainingcasestatus'),
            nullable=False,
        ),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['category_id'],
            ['conversationcategory.id'],
        ),
        sa.ForeignKeyConstraint(
            ['difficulty_id'],
            ['difficultylevel.id'],
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['userprofile.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'userconfidencescore',
        sa.Column('area_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['area_id'],
            ['confidencearea.id'],
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['userprofile.id'],
        ),
        sa.PrimaryKeyConstraint('area_id', 'user_id'),
    )
    op.create_table(
        'usergoal',
        sa.Column('goal_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['goal_id'],
            ['goal.id'],
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['userprofile.id'],
        ),
        sa.PrimaryKeyConstraint('goal_id', 'user_id'),
    )
    op.create_table(
        'trainingpreparation',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('case_id', sa.Uuid(), nullable=False),
        sa.Column('objectives', sa.JSON(), nullable=True),
        sa.Column('key_concepts', sa.JSON(), nullable=True),
        sa.Column('prep_checklist', sa.JSON(), nullable=True),
        sa.Column(
            'status',
            sa.Enum('pending', 'completed', 'failed', name='trainingpreparationstatus'),
            nullable=False,
        ),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['case_id'],
            ['trainingcase.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'trainingsession',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('case_id', sa.Uuid(), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('ended_at', sa.DateTime(), nullable=True),
        sa.Column('language_code', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('ai_persona', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['case_id'],
            ['trainingcase.id'],
        ),
        sa.ForeignKeyConstraint(
            ['language_code'],
            ['language.code'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'conversationturn',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('session_id', sa.Uuid(), nullable=False),
        sa.Column('speaker', sa.Enum('user', 'ai', name='speakerenum'), nullable=False),
        sa.Column('start_offset_ms', sa.Integer(), nullable=False),
        sa.Column('end_offset_ms', sa.Integer(), nullable=False),
        sa.Column('text', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('audio_uri', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('ai_emotion', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['session_id'],
            ['trainingsession.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'rating',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('session_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('comment', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['session_id'],
            ['trainingsession.id'],
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['userprofile.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'trainingsessionfeedback',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('session_id', sa.Uuid(), nullable=False),
        sa.Column('scores', sa.JSON(), nullable=True),
        sa.Column('tone_analysis', sa.JSON(), nullable=True),
        sa.Column('overall_score', sa.Integer(), nullable=False),
        sa.Column('transcript_uri', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('speak_time_percent', sa.Float(), nullable=False),
        sa.Column('questions_asked', sa.Integer(), nullable=False),
        sa.Column('session_length_s', sa.Integer(), nullable=False),
        sa.Column('goals_achieved', sa.Integer(), nullable=False),
        sa.Column('example_positive', sa.JSON(), nullable=True),
        sa.Column('example_negative', sa.JSON(), nullable=True),
        sa.Column('recommendations', sa.JSON(), nullable=True),
        sa.Column(
            'status',
            sa.Enum('pending', 'completed', 'failed', name='feedbackstatusenum'),
            nullable=False,
        ),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['session_id'],
            ['trainingsession.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'hr_information',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('content', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('metadata', sa.dialects.postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('embedding', Vector(dim=768), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('trainingsessionfeedback')
    op.drop_table('rating')
    op.drop_table('conversationturn')
    op.drop_table('trainingsession')
    op.drop_table('trainingpreparation')
    op.drop_table('usergoal')
    op.drop_table('userconfidencescore')
    op.drop_table('trainingcase')
    op.drop_table('userprofile')
    op.drop_table('conversationcategory')
    op.drop_table('sessionlength')
    op.drop_table('learningstyle')
    op.drop_table('language')
    op.drop_table('goal')
    op.drop_table('experience')
    op.drop_table('difficultylevel')
    op.drop_table('confidencearea')
    op.drop_table('appconfig')
    op.drop_table('hr_information')

    op.execute('DROP TYPE IF EXISTS configtype CASCADE')
    op.execute('DROP TYPE IF EXISTS userrole CASCADE')
    op.execute('DROP TYPE IF EXISTS trainingcasestatus CASCADE')
    op.execute('DROP TYPE IF EXISTS trainingpreparationstatus CASCADE')
    op.execute('DROP TYPE IF EXISTS speakerenum CASCADE')
    op.execute('DROP TYPE IF EXISTS feedbackstatusenum CASCADE')

    op.execute('DROP EXTENSION IF EXISTS vector CASCADE')
