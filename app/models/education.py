"""
SQLAlchemy models for education platform
All models as Python classes - no manual SQL as required by team lead
Updated for PostgreSQL with full schema support
"""

from datetime import datetime, date, time
from typing import Optional, List
from sqlalchemy import (
    Column, BigInteger, String, Text, Boolean, DateTime, Date, Time,
    ForeignKey, Table, Enum as SQLEnum, Integer, CheckConstraint, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.database import Base
import enum


# Enums
class MaterialCategory(str, enum.Enum):
    LECTURE = "lecture"  # Лекционные материалы
    ASSIGNMENT = "assignment"  # Задания
    METHODICAL = "methodical"  # Методические материалы


class SenderType(str, enum.Enum):
    USER = "user"
    BOT = "bot"


class AssignmentStatus(str, enum.Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    CHECKED = "checked"
    COMPLETED = "completed"


class MeetingType(str, enum.Enum):
    LECTURE = "lecture"  # Лекционная работа
    PRACTICE = "practice"  # Практическая работа
    INDEPENDENT = "independent"  # Самостоятельная работа


class PromptType(str, enum.Enum):
    QUESTION_CLASSIFIER = "question_classifier"
    FAQ_RESPONSE = "faq_response"
    MATERIAL_RESPONSE = "material_response"


# Association table for many-to-many relationship
students_streams = Table(
    'students_streams',
    Base.metadata,
    Column('student_id', BigInteger, ForeignKey('students.student_id', ondelete='CASCADE'), primary_key=True),
    Column('stream_id', BigInteger, ForeignKey('streams.stream_id', ondelete='CASCADE'), primary_key=True),
    Column('enrolled_at', DateTime(timezone=True), default=func.now())
)


class Student(Base):
    """Students table"""
    __tablename__ = "students"
    
    student_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    phone: Mapped[str] = mapped_column(String(15), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    telegram_user_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, unique=True)
    telegram_username: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    course_program_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey('course_programs.program_id'), nullable=True)
    
    # Relationships
    course_program: Mapped[Optional["CourseProgram"]] = relationship("CourseProgram", back_populates="students")
    streams: Mapped[List["Stream"]] = relationship("Stream", secondary=students_streams, back_populates="students")
    # messages: Mapped[List["Message"]] = relationship("Message", primaryjoin="Student.student_id == Message.sender_id", back_populates="student")
    assignments: Mapped[List["Assignment"]] = relationship("Assignment", back_populates="student")
    
    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint("phone ~ '^\\+?\\d{10,15}$'", name='check_phone_format'),
        Index('idx_students_phone', 'phone'),
        Index('idx_students_telegram_user_id', 'telegram_user_id'),
    )


class CourseProgram(Base):
    """Educational programs table"""
    __tablename__ = "course_programs"
    
    program_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    total_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    students: Mapped[List["Student"]] = relationship("Student", back_populates="course_program")
    streams: Mapped[List["Stream"]] = relationship("Stream", back_populates="program")
    modules: Mapped[List["Module"]] = relationship("Module", back_populates="program")


class Stream(Base):
    """Learning streams table"""
    __tablename__ = "streams"
    
    stream_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    program_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('course_programs.program_id', ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    program: Mapped["CourseProgram"] = relationship("CourseProgram", back_populates="streams")
    students: Mapped[List["Student"]] = relationship("Student", secondary=students_streams, back_populates="streams")
    meetings: Mapped[List["Meeting"]] = relationship("Meeting", back_populates="stream")
    schedule: Mapped[List["Schedule"]] = relationship("Schedule", back_populates="stream")


class Module(Base):
    """Course modules (sections) table"""
    __tablename__ = "modules"
    
    module_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    program_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('course_programs.program_id', ondelete='CASCADE'), nullable=False)
    order_num: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_hours: Mapped[int] = mapped_column(Integer, nullable=False)  # ДЛИТЕЛЬНОСТЬ РАЗДЕЛА
    lecture_hours: Mapped[int] = mapped_column(Integer, default=0)  # ЛЕКЦИОННЫЕ ЧАСЫ
    practice_hours: Mapped[int] = mapped_column(Integer, default=0)  # ПРАКТИЧЕСКИЕ ЧАСЫ
    independent_hours: Mapped[int] = mapped_column(Integer, default=0)  # САМОСТОЯТЕЛЬНЫЕ ЧАСЫ
    is_intermediate_attestation: Mapped[bool] = mapped_column(Boolean, default=False)  # ПРОМЕЖУТОЧНАЯ АТТЕСТАЦИЯ
    is_final_attestation: Mapped[bool] = mapped_column(Boolean, default=False)  # ИТОГОВАЯ АТТЕСТАЦИЯ
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    program: Mapped["CourseProgram"] = relationship("CourseProgram", back_populates="modules")
    lessons: Mapped[List["Lesson"]] = relationship("Lesson", back_populates="module")


class Lesson(Base):
    """Lessons (topics) within modules table"""
    __tablename__ = "lessons"
    
    lesson_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    module_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('modules.module_id', ondelete='CASCADE'), nullable=False)
    order_num: Mapped[int] = mapped_column(Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_hours: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    module: Mapped["Module"] = relationship("Module", back_populates="lessons")
    course_materials: Mapped[List["CourseMaterial"]] = relationship("CourseMaterial", back_populates="lesson")
    assignments: Mapped[List["Assignment"]] = relationship("Assignment", back_populates="lesson")
    meetings: Mapped[List["Meeting"]] = relationship("Meeting", back_populates="lesson")
    schedule: Mapped[List["Schedule"]] = relationship("Schedule", back_populates="lesson")


class CourseMaterial(Base):
    """Course materials table - 3 required types"""
    __tablename__ = "course_materials"
    
    material_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    lesson_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('lessons.lesson_id', ondelete='CASCADE'), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    material_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # PDF, VIDEO, TEXT, etc.
    material_category: Mapped[MaterialCategory] = mapped_column(SQLEnum(MaterialCategory), nullable=False)  # ТИП МАТЕРИАЛА
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="course_materials")
    
    # Indexes
    __table_args__ = (
        Index('idx_course_materials_lesson_id', 'lesson_id'),
        Index('idx_course_materials_material_type', 'material_type'),
    )


class Message(Base):
    """Messages from students table"""
    __tablename__ = "messages"
    
    message_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    telegram_message_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, unique=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sender_type: Mapped[SenderType] = mapped_column(SQLEnum(SenderType), nullable=False)
    sender_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    text_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attachment_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    # student: Mapped[Optional["Student"]] = relationship("Student", primaryjoin="Message.sender_id == Student.student_id", back_populates="messages")
    bot_responses: Mapped[List["BotResponse"]] = relationship("BotResponse", back_populates="message")
    
    # Indexes
    __table_args__ = (
        Index('idx_messages_chat_id', 'chat_id'),
        Index('idx_messages_telegram_message_id', 'telegram_message_id'),
    )


class BotResponse(Base):
    """Bot responses table (separate entity)"""
    __tablename__ = "bot_responses"
    
    response_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    message_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('messages.message_id', ondelete='CASCADE'), nullable=False)
    text_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attachment_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    message: Mapped["Message"] = relationship("Message", back_populates="bot_responses")


class Meeting(Base):
    """Meetings/classes table with types"""
    __tablename__ = "meetings"
    
    meeting_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    stream_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('streams.stream_id', ondelete='CASCADE'), nullable=False)
    lesson_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('lessons.lesson_id', ondelete='CASCADE'), nullable=False)
    meeting_type: Mapped[MeetingType] = mapped_column(SQLEnum(MeetingType), nullable=False)
    meeting_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)  # NULL для самостоятельной работы
    end_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)    # NULL для самостоятельной работы
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    stream: Mapped["Stream"] = relationship("Stream", back_populates="meetings")
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="meetings")


class Schedule(Base):
    """Schedule table (connection between streams and lessons with dates)"""
    __tablename__ = "schedule"
    
    schedule_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    stream_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('streams.stream_id', ondelete='CASCADE'), nullable=False)
    lesson_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('lessons.lesson_id', ondelete='CASCADE'), nullable=False)
    scheduled_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    stream: Mapped["Stream"] = relationship("Stream", back_populates="schedule")
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="schedule")
    
    # Indexes
    __table_args__ = (
        Index('idx_schedule_stream_id', 'stream_id'),
        Index('idx_schedule_scheduled_date', 'scheduled_date'),
    )


class Assignment(Base):
    """Student assignments table"""
    __tablename__ = "assignments"
    
    assignment_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('students.student_id', ondelete='CASCADE'), nullable=False)
    lesson_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('lessons.lesson_id', ondelete='CASCADE'), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[AssignmentStatus] = mapped_column(SQLEnum(AssignmentStatus), default=AssignmentStatus.PENDING, nullable=False)
    deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    checked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    grade: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="assignments")
    lesson: Mapped["Lesson"] = relationship("Lesson", back_populates="assignments")
    
    # Indexes
    __table_args__ = (
        Index('idx_assignments_student_id', 'student_id'),
        Index('idx_assignments_lesson_id', 'lesson_id'),
    )


class Prompt(Base):
    """AI prompts storage table"""
    __tablename__ = "prompts"
    
    prompt_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    prompt_type: Mapped[PromptType] = mapped_column(SQLEnum(PromptType), nullable=False)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    # Indexes
    __table_args__ = (
        Index('idx_prompts_type_active', 'prompt_type', 'is_active'),
    )


class FAQResponse(Base):
    """FAQ responses table (optional)"""
    __tablename__ = "faq_responses"
    
    faq_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    category: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    question: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)