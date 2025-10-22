"""Add indexes and constraints

Revision ID: 9c997ec8d589
Revises: d54c1882f365
Create Date: 2025-10-17 15:50:39.743092

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9c997ec8d589'
down_revision = 'd54c1882f365'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create indexes for students table
    op.create_index('idx_students_phone', 'students', ['phone'])
    op.create_index('idx_students_telegram_user_id', 'students', ['telegram_user_id'])
    
    # Create indexes for messages table
    op.create_index('idx_messages_chat_id', 'messages', ['chat_id'])
    op.create_index('idx_messages_telegram_message_id', 'messages', ['telegram_message_id'])
    
    # Create indexes for assignments table
    op.create_index('idx_assignments_student_id', 'assignments', ['student_id'])
    op.create_index('idx_assignments_lesson_id', 'assignments', ['lesson_id'])
    
    # Create indexes for course_materials table
    op.create_index('idx_course_materials_lesson_id', 'course_materials', ['lesson_id'])
    op.create_index('idx_course_materials_material_type', 'course_materials', ['material_type'])
    
    # Create indexes for schedule table
    op.create_index('idx_schedule_stream_id', 'schedule', ['stream_id'])
    op.create_index('idx_schedule_scheduled_date', 'schedule', ['scheduled_date'])
    
    # Create indexes for prompts table
    op.create_index('idx_prompts_type_active', 'prompts', ['prompt_type', 'is_active'])
    
    # Add check constraint for phone format
    op.create_check_constraint(
        'check_phone_format',
        'students',
        "phone ~ '^\\+?\\d{10,15}$'"
    )
    
    # Change enrolled_at column type to timestamp with time zone
    op.alter_column('students_streams', 'enrolled_at',
                   existing_type=sa.DateTime(),
                   type_=sa.DateTime(timezone=True),
                   existing_nullable=True)
    
    # Create PromptType enum if it doesn't exist
    prompt_type_enum = sa.Enum('QUESTION_CLASSIFIER', 'FAQ_RESPONSE', 'MATERIAL_RESPONSE', name='prompttype')
    prompt_type_enum.create(op.get_bind())
    
    # Change prompt_type column to use enum
    op.alter_column('prompts', 'prompt_type',
                   existing_type=sa.String(50),
                   type_=prompt_type_enum,
                   existing_nullable=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_prompts_type_active', 'prompts')
    op.drop_index('idx_schedule_scheduled_date', 'schedule')
    op.drop_index('idx_schedule_stream_id', 'schedule')
    op.drop_index('idx_course_materials_material_type', 'course_materials')
    op.drop_index('idx_course_materials_lesson_id', 'course_materials')
    op.drop_index('idx_assignments_lesson_id', 'assignments')
    op.drop_index('idx_assignments_student_id', 'assignments')
    op.drop_index('idx_messages_telegram_message_id', 'messages')
    op.drop_index('idx_messages_chat_id', 'messages')
    op.drop_index('idx_students_telegram_user_id', 'students')
    op.drop_index('idx_students_phone', 'students')
    
    # Drop check constraint
    op.drop_constraint('check_phone_format', 'students', type_='check')
    
    # Revert enrolled_at column type
    op.alter_column('students_streams', 'enrolled_at',
                   existing_type=sa.DateTime(timezone=True),
                   type_=sa.DateTime(),
                   existing_nullable=True)
    
    # Revert prompt_type column to string
    op.alter_column('prompts', 'prompt_type',
                   existing_type=sa.Enum('QUESTION_CLASSIFIER', 'FAQ_RESPONSE', 'MATERIAL_RESPONSE', name='prompttype'),
                   type_=sa.String(50),
                   existing_nullable=False)
    
    # Drop PromptType enum
    sa.Enum(name='prompttype').drop(op.get_bind())
