"""Add stream notification config

Revision ID: a1b2c3d4e5f6
Revises: d54c1882f365
Create Date: 2025-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'd54c1882f365'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create stream_notification_configs table
    op.create_table(
        'stream_notification_configs',
        sa.Column('config_id', sa.BigInteger(), nullable=False),
        sa.Column('stream_id', sa.BigInteger(), nullable=False),
        sa.Column('notification_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('frequency', sa.String(length=20), nullable=False, server_default='weekly'),
        sa.Column('day_of_week', sa.Integer(), nullable=True),
        sa.Column('time', sa.Time(), nullable=True),
        sa.Column('student_limit', sa.Integer(), nullable=True),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='ru'),
        sa.Column('tone', sa.String(length=20), nullable=False, server_default='friendly'),
        sa.Column('anti_repeat_rules', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('dry_run_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['stream_id'], ['streams.stream_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('config_id'),
        sa.UniqueConstraint('stream_id')
    )
    
    # Create index on stream_id
    op.create_index('idx_stream_notification_config_stream_id', 'stream_notification_configs', ['stream_id'], unique=False)
    
    # Create index on config_id
    op.create_index(op.f('ix_stream_notification_configs_config_id'), 'stream_notification_configs', ['config_id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_stream_notification_configs_config_id'), table_name='stream_notification_configs')
    op.drop_index('idx_stream_notification_config_stream_id', table_name='stream_notification_configs')
    
    # Drop table
    op.drop_table('stream_notification_configs')

