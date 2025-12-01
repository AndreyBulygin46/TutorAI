"""
Pydantic schemas for Rating and n8n Integration API
"""
from datetime import date, datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from app.schemas.student import StudentFacts


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


class StreamNotificationConfigBase(BaseModel):
    """Базовая схема конфигурации уведомлений потока"""
    notification_enabled: bool = Field(True, description="Включены ли уведомления")
    frequency: str = Field("weekly", description="Частота рассылки: weekly, daily")
    day_of_week: Optional[int] = Field(None, ge=0, le=6, description="День недели (0-6, понедельник-воскресенье)")
    time: Optional[str] = Field(None, description="Время рассылки (HH:MM)")
    student_limit: Optional[int] = Field(None, ge=1, description="Лимит выборки студентов")
    language: str = Field("ru", description="Язык сообщений")
    tone: str = Field("friendly", description="Тон сообщений: friendly, formal, supportive")
    anti_repeat_rules: Optional[Dict[str, Any]] = Field(None, description="Правила антиповтора (JSON)")
    dry_run_enabled: bool = Field(False, description="Режим сухого прогона")


class StreamNotificationConfigCreate(StreamNotificationConfigBase):
    """Схема для создания конфигурации"""
    stream_id: int = Field(..., description="ID потока")


class StreamNotificationConfigUpdate(BaseModel):
    """Схема для обновления конфигурации"""
    notification_enabled: Optional[bool] = None
    frequency: Optional[str] = None
    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    time: Optional[str] = None
    student_limit: Optional[int] = Field(None, ge=1)
    language: Optional[str] = None
    tone: Optional[str] = None
    anti_repeat_rules: Optional[Dict[str, Any]] = None
    dry_run_enabled: Optional[bool] = None


class StreamNotificationConfigResponse(StreamNotificationConfigBase):
    """Схема ответа для конфигурации"""
    model_config = ConfigDict(from_attributes=True)
    
    config_id: int = Field(..., description="ID конфигурации")
    stream_id: int = Field(..., description="ID потока")
    time: Optional[str] = Field(None, description="Время рассылки (HH:MM)")
    created_at: datetime = Field(..., description="Дата создания")
    updated_at: datetime = Field(..., description="Дата обновления")


class StreamConfig(BaseModel):
    """Конфигурация потока для n8n"""
    stream_id: int
    name: str
    program_id: int
    start_date: date
    end_date: date
    is_active: bool = True
    rating_config: Optional[RatingConfig] = None
    notification_config: Optional[StreamNotificationConfigResponse] = Field(None, description="Конфигурация уведомлений")
    notification_settings: Dict[str, Any] = Field(default_factory=dict)  # Для обратной совместимости


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


class StreamStudentsFactsResponse(BaseModel):
    """Факты недели для всех студентов потока"""
    stream_id: int
    week_start: date
    week_end: date
    students_facts: List[StudentFacts] = Field(..., description="Факты для каждого студента")
    total_students: int
    active_students: int