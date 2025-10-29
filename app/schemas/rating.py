"""
Pydantic schemas for Rating and n8n Integration API
"""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


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


class StudentFacts(BaseModel):
    """Факты о студенте за период"""
    student_id: int
    week_start: date
    week_end: date
    assignments: Dict[str, Any] = Field(..., description="Данные по заданиям")
    activity: Dict[str, Any] = Field(..., description="Данные по активности")
    attendance: Dict[str, Any] = Field(..., description="Данные по посещаемости")
    engagement: Dict[str, Any] = Field(..., description="Данные по вовлеченности")


class WeeklyRating(BaseModel):
    """Недельный рейтинг студента"""
    student_id: int
    week_start: date
    week_end: date
    weekly_score: float = Field(..., ge=0, le=100, description="Недельный рейтинг")
    assignment_score: float = Field(..., ge=0, le=100, description="Рейтинг по заданиям")
    activity_score: float = Field(..., ge=0, le=100, description="Рейтинг по активности")
    attendance_score: float = Field(..., ge=0, le=100, description="Рейтинг по посещаемости")
    engagement_score: float = Field(..., ge=0, le=100, description="Рейтинг по вовлеченности")
    category: str = Field(..., description="Категория рейтинга")
    recommendations: List[str] = Field(..., description="Рекомендации")
    personal_message: str = Field(..., description="Персональное сообщение")
    calculated_at: datetime = Field(default_factory=datetime.now)


class RatingCalculationRequest(BaseModel):
    """Запрос на расчет рейтинга"""
    student_ids: List[int] = Field(..., description="ID студентов")
    week_start: date = Field(..., description="Начало недели")
    week_end: date = Field(..., description="Конец недели")
    config: Optional[RatingConfig] = Field(None, description="Конфигурация расчета")


class RatingCalculationResponse(BaseModel):
    """Ответ на расчет рейтинга"""
    ratings: List[WeeklyRating]
    total_students: int
    calculated_at: datetime = Field(default_factory=datetime.now)


class StreamConfig(BaseModel):
    """Конфигурация потока для n8n"""
    stream_id: int
    name: str
    program_id: int
    start_date: date
    end_date: date
    is_active: bool = True
    rating_config: Optional[RatingConfig] = None
    notification_settings: Dict[str, Any] = Field(default_factory=dict)


class N8nNotificationRequest(BaseModel):
    """Запрос на отправку уведомлений через n8n"""
    stream_id: int
    student_ids: List[int]
    message_template: str
    notification_type: str = Field(..., description="Тип уведомления")
    send_immediately: bool = False
    scheduled_time: Optional[datetime] = None


class N8nNotificationResponse(BaseModel):
    """Ответ на отправку уведомлений"""
    success: bool
    sent_count: int
    failed_count: int
    errors: List[str] = Field(default_factory=list)
    sent_at: datetime = Field(default_factory=datetime.now)


class StreamStudentsResponse(BaseModel):
    """Студенты потока для n8n"""
    stream_id: int
    students: List[Dict[str, Any]]
    total_count: int
    active_count: int


class WeeklyReport(BaseModel):
    """Еженедельный отчет по потоку"""
    stream_id: int
    week_start: date
    week_end: date
    total_students: int
    active_students: int
    average_rating: float
    top_performers: List[Dict[str, Any]]
    needs_attention: List[Dict[str, Any]]
    generated_at: datetime = Field(default_factory=datetime.now)
