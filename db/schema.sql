-- PostgreSQL Schema for AI Tutor Backend
-- This file contains the complete database schema

-- Create ENUM types
CREATE TYPE materialcategory AS ENUM ('lecture', 'assignment', 'methodical');
CREATE TYPE sendertype AS ENUM ('user', 'bot');
CREATE TYPE assignmentstatus AS ENUM ('pending', 'submitted', 'checked', 'completed');
CREATE TYPE meetingtype AS ENUM ('lecture', 'practice', 'independent');
CREATE TYPE prompttype AS ENUM ('question_classifier', 'faq_response', 'material_response');

-- Students table
CREATE TABLE students (
    student_id BIGSERIAL PRIMARY KEY,
    phone VARCHAR(15) NOT NULL UNIQUE CHECK (phone ~ '^\+?\d{10,15}$'),
    name VARCHAR(100) NOT NULL,
    telegram_user_id BIGINT UNIQUE,
    telegram_username VARCHAR(50),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_login_at TIMESTAMPTZ,
    course_program_id BIGINT
);

-- Course programs table
CREATE TABLE course_programs (
    program_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    total_hours INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Streams table
CREATE TABLE streams (
    stream_id BIGSERIAL PRIMARY KEY,
    program_id BIGINT REFERENCES course_programs(program_id) ON DELETE CASCADE,
    name VARCHAR(150) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Students-Streams association table
CREATE TABLE students_streams (
    student_id BIGINT REFERENCES students(student_id) ON DELETE CASCADE,
    stream_id BIGINT REFERENCES streams(stream_id) ON DELETE CASCADE,
    enrolled_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (student_id, stream_id)
);

-- Messages table
CREATE TABLE messages (
    message_id BIGSERIAL PRIMARY KEY,
    telegram_message_id BIGINT UNIQUE,
    chat_id BIGINT NOT NULL,
    sender_type sendertype NOT NULL,
    sender_id BIGINT,
    text_content TEXT,
    attachment_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Bot responses table
CREATE TABLE bot_responses (
    response_id BIGSERIAL PRIMARY KEY,
    message_id BIGINT REFERENCES messages(message_id) ON DELETE CASCADE,
    text_content TEXT,
    attachment_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Modules table
CREATE TABLE modules (
    module_id BIGSERIAL PRIMARY KEY,
    program_id BIGINT REFERENCES course_programs(program_id) ON DELETE CASCADE,
    order_num INTEGER NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    duration_hours INTEGER NOT NULL,
    lecture_hours INTEGER DEFAULT 0,
    practice_hours INTEGER DEFAULT 0,
    independent_hours INTEGER DEFAULT 0,
    is_intermediate_attestation BOOLEAN DEFAULT FALSE,
    is_final_attestation BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Lessons table
CREATE TABLE lessons (
    lesson_id BIGSERIAL PRIMARY KEY,
    module_id BIGINT REFERENCES modules(module_id) ON DELETE CASCADE,
    order_num INTEGER NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    duration_hours INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Course materials table
CREATE TABLE course_materials (
    material_id BIGSERIAL PRIMARY KEY,
    lesson_id BIGINT REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    content TEXT,
    file_path VARCHAR(255),
    material_type VARCHAR(50),
    material_category materialcategory NOT NULL,
    is_public BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Meetings table
CREATE TABLE meetings (
    meeting_id BIGSERIAL PRIMARY KEY,
    stream_id BIGINT REFERENCES streams(stream_id) ON DELETE CASCADE,
    lesson_id BIGINT REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    meeting_type meetingtype NOT NULL,
    meeting_date DATE NOT NULL,
    start_time TIME,
    end_time TIME,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Schedule table
CREATE TABLE schedule (
    schedule_id BIGSERIAL PRIMARY KEY,
    stream_id BIGINT REFERENCES streams(stream_id) ON DELETE CASCADE,
    lesson_id BIGINT REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    scheduled_date DATE NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Assignments table
CREATE TABLE assignments (
    assignment_id BIGSERIAL PRIMARY KEY,
    student_id BIGINT REFERENCES students(student_id) ON DELETE CASCADE,
    lesson_id BIGINT REFERENCES lessons(lesson_id) ON DELETE CASCADE,
    name VARCHAR(150),
    description TEXT,
    status assignmentstatus NOT NULL DEFAULT 'pending',
    deadline DATE,
    submitted_at TIMESTAMPTZ,
    checked_at TIMESTAMPTZ,
    feedback TEXT,
    grade INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Prompts table
CREATE TABLE prompts (
    prompt_id BIGSERIAL PRIMARY KEY,
    prompt_type prompttype NOT NULL,
    prompt_text TEXT NOT NULL,
    description TEXT,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- FAQ responses table
CREATE TABLE faq_responses (
    faq_id BIGSERIAL PRIMARY KEY,
    category VARCHAR(50),
    keywords TEXT,
    question TEXT,
    answer_text TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Add foreign key constraint for students.course_program_id
ALTER TABLE students ADD CONSTRAINT fk_students_course_program 
FOREIGN KEY (course_program_id) REFERENCES course_programs(program_id);

-- Create indexes for optimization
CREATE INDEX idx_students_phone ON students(phone);
CREATE INDEX idx_students_telegram_user_id ON students(telegram_user_id);
CREATE INDEX idx_messages_chat_id ON messages(chat_id);
CREATE INDEX idx_messages_telegram_message_id ON messages(telegram_message_id);
CREATE INDEX idx_modules_program_id ON modules(program_id);
CREATE INDEX idx_lessons_module_id ON lessons(module_id);
CREATE INDEX idx_course_materials_lesson_id ON course_materials(lesson_id);
CREATE INDEX idx_course_materials_material_type ON course_materials(material_type);
CREATE INDEX idx_meetings_stream_id ON meetings(stream_id);
CREATE INDEX idx_meetings_date ON meetings(meeting_date);
CREATE INDEX idx_schedule_stream_id ON schedule(stream_id);
CREATE INDEX idx_schedule_scheduled_date ON schedule(scheduled_date);
CREATE INDEX idx_assignments_student_id ON assignments(student_id);
CREATE INDEX idx_assignments_lesson_id ON assignments(lesson_id);
CREATE INDEX idx_prompts_type_active ON prompts(prompt_type, is_active);

-- Create trigger function for auto-updating updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for auto-updating updated_at
CREATE TRIGGER update_students_updated_at 
    BEFORE UPDATE ON students 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prompts_updated_at 
    BEFORE UPDATE ON prompts 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
