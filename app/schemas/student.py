"""
Pydantic schemas for Student API
"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class StudentBase(BaseModel):
    """Базовая схема студента"""
    name: str = Field(..., min_length=1, max_length=100, description="Имя студента")
    phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$', description="Номер телефона")
    telegram_user_id: Optional[int] = Field(None, description="Telegram User ID")
    telegram_username: Optional[str] = Field(None, max_length=50, description="Telegram username")
    is_active: bool = Field(True, description="Активен ли студент")
    course_program_id: Optional[int] = Field(None, description="ID программы курса")


class StudentCreate(StudentBase):
    """Схема для создания студента"""
    pass


class StudentUpdate(BaseModel):
    """Схема для обновления студента"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    telegram_user_id: Optional[int] = None
    telegram_username: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    course_program_id: Optional[int] = None


class StudentResponse(StudentBase):
    """Схема ответа для студента"""
    model_config = ConfigDict(from_attributes=True)
    
    student_id: int = Field(..., description="ID студента")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")
    last_login_at: Optional[datetime] = Field(None, description="Последний вход")


class StudentListResponse(BaseModel):
    """Схема для списка студентов"""
    students: List[StudentResponse]
    total: int = Field(..., description="Общее количество студентов")
    page: int = Field(..., description="Текущая страница")
    size: int = Field(..., description="Размер страницы")


class StudentFacts(BaseModel):
    """Факты о студенте за период"""
    student_id: int
    week_start: date
    week_end: date
    assignments: dict = Field(..., description="Данные по заданиям")
    activity: dict = Field(..., description="Данные по активности")
    attendance: dict = Field(..., description="Данные по посещаемости")
    engagement: dict = Field(..., description="Данные по вовлеченности")


class StudentRating(BaseModel):
    """Рейтинг студента"""
    student_id: int
    weekly_score: float = Field(..., ge=0, le=100, description="Недельный рейтинг")
    assignment_score: float = Field(..., ge=0, le=100, description="Рейтинг по заданиям")
    activity_score: float = Field(..., ge=0, le=100, description="Рейтинг по активности")
    attendance_score: float = Field(..., ge=0, le=100, description="Рейтинг по посещаемости")
    engagement_score: float = Field(..., ge=0, le=100, description="Рейтинг по вовлеченности")
    category: str = Field(..., description="Категория рейтинга")
    recommendations: List[str] = Field(..., description="Рекомендации")
    message: str = Field(..., description="Персональное сообщение")


class StudentStats(BaseModel):
    """Статистика студента"""
    student_id: int
    total_assignments: int
    completed_assignments: int
    average_grade: Optional[float]
    messages_count: int
    attendance_rate: float
    study_hours: float
    last_activity: Optional[datetime]


class RatingConfig(BaseModel):
    """Конфигурация для расчета рейтинга"""
    assignment_weight: float = Field(0.4, ge=0, le=1, description="Вес заданий")
    activity_weight: float = Field(0.3, ge=0, le=1, description="Вес активности")
    attendance_weight: float = Field(0.2, ge=0, le=1, description="Вес посещаемости")
    engagement_weight: float = Field(0.1, ge=0, le=1, description="Вес вовлеченности")
    
    def model_post_init(self, __context):
        total = (self.assignment_weight + self.activity_weight + 
                self.attendance_weight + self.engagement_weight)
        if abs(total - 1.0) > 0.01:
            raise ValueError("Сумма весов должна равняться 1.0")
