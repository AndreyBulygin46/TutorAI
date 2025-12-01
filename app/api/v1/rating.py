"""
Rating API for student rating calculation and n8n integration
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.services.student_service import StudentService
from app.models.education import Student, Stream, StreamNotificationConfig
from app.schemas.student import StudentFacts
from app.schemas.rating import (
    RatingCalculationRequest, RatingCalculationResponse, WeeklyRating,
    StreamConfig, StreamStudentsResponse, WeeklyReport, N8nNotificationRequest,
    N8nNotificationResponse, StreamStudentsFactsResponse,
    StreamNotificationConfigCreate, StreamNotificationConfigUpdate,
    StreamNotificationConfigResponse
)

# TODO: Раскомментировать для продакшена
# from app.core.auth import verify_api_key

# TODO: Раскомментировать dependencies для продакшена
router = APIRouter(prefix="/rating", tags=["rating"])
# router = APIRouter(
#     prefix="/rating", 
#     tags=["rating"],
#     dependencies=[Depends(verify_api_key)]  # Проверка API ключа для всех эндпоинтов
# )


@router.post("/calculate", response_model=RatingCalculationResponse)
async def calculate_ratings(
    request: RatingCalculationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Рассчитать рейтинги для списка студентов"""
    service = StudentService(db)
    ratings = []
    
    for student_id in request.student_ids:
        # Проверяем, что студент существует
        student = await service.get_student_by_id(student_id)
        if not student:
            continue
        
        # Рассчитываем рейтинг
        rating = await service.calculate_student_rating(
            student_id, 
            request.week_start, 
            request.week_end,
            request.config
        )
        
        # Конвертируем в WeeklyRating
        weekly_rating = WeeklyRating(
            student_id=rating.student_id,
            week_start=request.week_start,
            week_end=request.week_end,
            weekly_score=rating.weekly_score,
            assignment_score=rating.assignment_score,
            activity_score=rating.activity_score,
            attendance_score=rating.attendance_score,
            engagement_score=rating.engagement_score,
            category=rating.category,
            recommendations=rating.recommendations,
            personal_message=rating.message
        )
        
        ratings.append(weekly_rating)
    
    return RatingCalculationResponse(
        ratings=ratings,
        total_students=len(ratings)
    )


@router.get("/student/{student_id}/weekly", response_model=WeeklyRating)
async def get_student_weekly_rating(
    student_id: int,
    week_start: date = Query(..., description="Начало недели"),
    week_end: date = Query(..., description="Конец недели"),
    db: AsyncSession = Depends(get_db)
):
    """Получить недельный рейтинг студента"""
    service = StudentService(db)
    
    # Проверяем, что студент существует
    student = await service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    # Рассчитываем рейтинг
    rating = await service.calculate_student_rating(student_id, week_start, week_end)
    
    return WeeklyRating(
        student_id=rating.student_id,
        week_start=week_start,
        week_end=week_end,
        weekly_score=rating.weekly_score,
        assignment_score=rating.assignment_score,
        activity_score=rating.activity_score,
        attendance_score=rating.attendance_score,
        engagement_score=rating.engagement_score,
        category=rating.category,
        recommendations=rating.recommendations,
        personal_message=rating.message
    )


@router.get("/streams", response_model=List[StreamConfig])
async def get_streams_config(
    db: AsyncSession = Depends(get_db)
):
    """Получить конфигурацию потоков для n8n"""
    # Получаем все активные потоки с конфигурацией
    query = select(Stream).where(Stream.end_date >= date.today())
    result = await db.execute(query)
    streams = result.scalars().all()
    
    configs = []
    for stream in streams:
        # Получаем конфигурацию уведомлений из БД
        notification_config_query = select(StreamNotificationConfig).where(
            StreamNotificationConfig.stream_id == stream.stream_id
        )
        notification_config_result = await db.execute(notification_config_query)
        notification_config = notification_config_result.scalar_one_or_none()
        
        # Если конфигурации нет, используем значения по умолчанию
        if notification_config:
            # Конвертируем time в строку для ответа
            notification_config_dict = {
                "config_id": notification_config.config_id,
                "stream_id": notification_config.stream_id,
                "notification_enabled": notification_config.notification_enabled,
                "frequency": notification_config.frequency,
                "day_of_week": notification_config.day_of_week,
                "time": notification_config.time.strftime("%H:%M") if notification_config.time else None,
                "student_limit": notification_config.student_limit,
                "language": notification_config.language,
                "tone": notification_config.tone,
                "anti_repeat_rules": notification_config.anti_repeat_rules,
                "dry_run_enabled": notification_config.dry_run_enabled,
                "created_at": notification_config.created_at,
                "updated_at": notification_config.updated_at,
            }
            notification_config_response = StreamNotificationConfigResponse(**notification_config_dict)
            notification_settings = {
                "enabled": notification_config.notification_enabled,
                "schedule": notification_config.frequency,
                "day_of_week": notification_config.day_of_week,
                "time": notification_config.time.strftime("%H:%M") if notification_config.time else None,
                "student_limit": notification_config.student_limit,
                "language": notification_config.language,
                "tone": notification_config.tone,
                "dry_run_enabled": notification_config.dry_run_enabled
            }
        else:
            notification_config_response = None
            notification_settings = {
                "enabled": True,
                "schedule": "weekly",
                "day_of_week": 1,  # Понедельник
                "time": "10:00"
            }
        
        config = StreamConfig(
            stream_id=stream.stream_id,
            name=stream.name,
            program_id=stream.program_id,
            start_date=stream.start_date,
            end_date=stream.end_date,
            is_active=stream.end_date >= date.today(),
            notification_config=notification_config_response,
            notification_settings=notification_settings  # Для обратной совместимости
        )
        configs.append(config)
    
    return configs


@router.get("/streams/{stream_id}/students", response_model=StreamStudentsResponse)
async def get_stream_students(
    stream_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить студентов потока для n8n"""
    # Получаем поток
    stream_query = select(Stream).where(Stream.stream_id == stream_id)
    stream_result = await db.execute(stream_query)
    stream = stream_result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(status_code=404, detail="Поток не найден")
    
    # Получаем студентов потока
    students_query = select(Student).join(Student.streams).where(
        Stream.stream_id == stream_id
    )
    students_result = await db.execute(students_query)
    students = students_result.scalars().all()
    
    # Конвертируем в формат для n8n
    students_data = []
    active_count = 0
    
    for student in students:
        if student.is_active is True:
            active_count += 1
        
        student_data = {
            "student_id": student.student_id,
            "name": student.name,
            "phone": student.phone,
            "telegram_user_id": student.telegram_user_id,
            "telegram_username": student.telegram_username,
            "is_active": student.is_active,
            "course_program_id": student.course_program_id,
            "created_at": student.created_at.isoformat() if student.created_at else None,
            "last_login_at": student.last_login_at.isoformat() if student.last_login_at else None
        }
        students_data.append(student_data)
    
    return StreamStudentsResponse(
        stream_id=stream_id,
        students=students_data,
        total_count=len(students_data),
        active_count=active_count
    )


@router.get("/streams/{stream_id}/students-facts", response_model=StreamStudentsFactsResponse)
async def get_stream_students_facts(
    stream_id: int,
    week_start: date = Query(..., description="Начало недели"),
    week_end: date = Query(..., description="Конец недели"),
    db: AsyncSession = Depends(get_db)
):
    """Получить факты недели для всех студентов потока (для n8n)"""
    # Получаем поток
    stream_query = select(Stream).where(Stream.stream_id == stream_id)
    stream_result = await db.execute(stream_query)
    stream = stream_result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(status_code=404, detail="Поток не найден")
    
    # Получаем студентов потока
    students_query = select(Student).join(Student.streams).where(
        Stream.stream_id == stream_id
    )
    students_result = await db.execute(students_query)
    students = students_result.scalars().all()
    
    # Получаем факты для каждого студента
    service = StudentService(db)
    students_facts = []
    active_count = 0
    
    for student in students:
        if not student.is_active:
            continue
        
        active_count += 1
        
        try:
            facts = await service.get_student_facts(
                student.student_id,
                week_start,
                week_end
            )
            students_facts.append(facts)
        except Exception as e:
            # Логируем ошибку, но продолжаем обработку других студентов
            # В продакшене можно добавить логирование
            continue
    
    return StreamStudentsFactsResponse(
        stream_id=stream_id,
        week_start=week_start,
        week_end=week_end,
        students_facts=students_facts,
        total_students=len(students),
        active_students=active_count
    )


@router.get("/streams/{stream_id}/weekly-report", response_model=WeeklyReport)
async def get_weekly_report(
    stream_id: int,
    week_start: Optional[date] = Query(None, description="Начало недели"),
    week_end: Optional[date] = Query(None, description="Конец недели"),
    db: AsyncSession = Depends(get_db)
):
    """Получить еженедельный отчет по потоку"""
    # Если даты не указаны, используем прошлую неделю
    if not week_start or not week_end:
        today = date.today()
        week_start = today - timedelta(days=today.weekday() + 7)
        week_end = week_start + timedelta(days=6)
    
    # Получаем поток
    stream_query = select(Stream).where(Stream.stream_id == stream_id)
    stream_result = await db.execute(stream_query)
    stream = stream_result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(status_code=404, detail="Поток не найден")
    
    # Получаем студентов потока
    students_query = select(Student).join(Student.streams).where(
        Stream.stream_id == stream_id
    )
    students_result = await db.execute(students_query)
    students = students_result.scalars().all()
    
    service = StudentService(db)
    ratings = []
    
    # Рассчитываем рейтинги для всех студентов
    for student in students:
        if not student.is_active:
            continue
        
        try:
            rating = await service.calculate_student_rating(
                student.student_id, week_start, week_end
            )
            ratings.append(rating)
        except Exception:
            continue  # Пропускаем студентов с ошибками
    
    if not ratings:
        return WeeklyReport(
            stream_id=stream_id,
            week_start=week_start,
            week_end=week_end,
            total_students=len(students),
            active_students=0,
            average_rating=0.0,
            top_performers=[],
            needs_attention=[]
        )
    
    # Сортируем по рейтингу
    ratings.sort(key=lambda x: x.weekly_score, reverse=True)
    
    # Топ-3 студента
    top_performers = [
        {
            "student_id": r.student_id,
            "weekly_score": r.weekly_score,
            "category": r.category
        }
        for r in ratings[:3]
    ]
    
    # Студенты, требующие внимания (рейтинг < 50)
    needs_attention = [
        {
            "student_id": r.student_id,
            "weekly_score": r.weekly_score,
            "category": r.category,
            "recommendations": r.recommendations[:2]  # Первые 2 рекомендации
        }
        for r in ratings if r.weekly_score < 50
    ]
    
    # Средний рейтинг
    average_rating = sum(r.weekly_score for r in ratings) / len(ratings)
    
    return WeeklyReport(
        stream_id=stream_id,
        week_start=week_start,
        week_end=week_end,
        total_students=len(students),
        active_students=len(ratings),
        average_rating=round(average_rating, 2),
        top_performers=top_performers,
        needs_attention=needs_attention
    )


@router.post("/notifications/send", response_model=N8nNotificationResponse)
async def send_notifications(
    request: N8nNotificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Отправить уведомления студентам (заглушка для n8n)"""
    # В реальной реализации здесь будет интеграция с Telegram Bot API
    # Пока возвращаем заглушку
    
    sent_count = 0
    failed_count = 0
    errors = []
    
    # Проверяем, что поток существует
    stream_query = select(Stream).where(Stream.stream_id == request.stream_id)
    stream_result = await db.execute(stream_query)
    stream = stream_result.scalar_one_or_none()
    
    if not stream:
        return N8nNotificationResponse(
            success=False,
            sent_count=0,
            failed_count=len(request.student_ids),
            errors=["Поток не найден"]
        )
    
    # Получаем студентов
    students_query = select(Student).where(
        and_(
            Student.student_id.in_(request.student_ids),
            Student.is_active == True
        )
    )
    students_result = await db.execute(students_query)
    students = students_result.scalars().all()
    
    # В реальной реализации здесь будет отправка через Telegram
    for student in students:
        if student.telegram_user_id:
            # Заглушка: считаем, что отправка успешна
            sent_count += 1
        else:
            failed_count += 1
            errors.append(f"Студент {student.name} не имеет Telegram ID")
    
    return N8nNotificationResponse(
        success=failed_count == 0,
        sent_count=sent_count,
        failed_count=failed_count,
        errors=errors
    )


@router.get("/streams/{stream_id}/config", response_model=StreamNotificationConfigResponse)
async def get_stream_notification_config(
    stream_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить конфигурацию уведомлений потока"""
    # Проверяем, что поток существует
    stream_query = select(Stream).where(Stream.stream_id == stream_id)
    stream_result = await db.execute(stream_query)
    stream = stream_result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(status_code=404, detail="Поток не найден")
    
    # Получаем конфигурацию
    config_query = select(StreamNotificationConfig).where(
        StreamNotificationConfig.stream_id == stream_id
    )
    config_result = await db.execute(config_query)
    config = config_result.scalar_one_or_none()
    
    # Если конфигурации нет, возвращаем дефолтные значения (как в get_streams_config)
    if not config:
        # Дефолтные значения из модели StreamNotificationConfig
        return StreamNotificationConfigResponse(
            config_id=0,  # Временный ID, так как записи в БД нет
            stream_id=stream_id,
            notification_enabled=True,
            frequency="weekly",
            day_of_week=1,  # Понедельник
            time="10:00",
            student_limit=None,
            language="ru",
            tone="friendly",
            anti_repeat_rules=None,
            dry_run_enabled=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    # Конвертируем time в строку для ответа
    config_dict = {
        "config_id": config.config_id,
        "stream_id": config.stream_id,
        "notification_enabled": config.notification_enabled,
        "frequency": config.frequency,
        "day_of_week": config.day_of_week,
        "time": config.time.strftime("%H:%M") if config.time else None,
        "student_limit": config.student_limit,
        "language": config.language,
        "tone": config.tone,
        "anti_repeat_rules": config.anti_repeat_rules,
        "dry_run_enabled": config.dry_run_enabled,
        "created_at": config.created_at,
        "updated_at": config.updated_at,
    }
    return StreamNotificationConfigResponse(**config_dict)


@router.put("/streams/{stream_id}/config", response_model=StreamNotificationConfigResponse)
async def update_stream_notification_config(
    stream_id: int,
    config_data: StreamNotificationConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить конфигурацию уведомлений потока"""
    # Проверяем, что поток существует
    stream_query = select(Stream).where(Stream.stream_id == stream_id)
    stream_result = await db.execute(stream_query)
    stream = stream_result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(status_code=404, detail="Поток не найден")
    
    # Получаем существующую конфигурацию или создаем новую
    config_query = select(StreamNotificationConfig).where(
        StreamNotificationConfig.stream_id == stream_id
    )
    config_result = await db.execute(config_query)
    config = config_result.scalar_one_or_none()
    
    if not config:
        # Создаем новую конфигурацию с дефолтными значениями
        config = StreamNotificationConfig(
            stream_id=stream_id,
            **config_data.model_dump(exclude_unset=True)
        )
        db.add(config)
    else:
        # Обновляем существующую конфигурацию
        update_data = config_data.model_dump(exclude_unset=True)
        
        # Обработка времени (конвертация строки в time объект)
        if "time" in update_data and update_data["time"]:
            from datetime import datetime as dt
            time_obj = dt.strptime(update_data["time"], "%H:%M").time()
            update_data["time"] = time_obj
        
        for field, value in update_data.items():
            setattr(config, field, value)
        
        config.updated_at = datetime.now()
    
    await db.commit()
    await db.refresh(config)
    
    # Конвертируем time в строку для ответа
    config_dict = {
        "config_id": config.config_id,
        "stream_id": config.stream_id,
        "notification_enabled": config.notification_enabled,
        "frequency": config.frequency,
        "day_of_week": config.day_of_week,
        "time": config.time.strftime("%H:%M") if config.time else None,
        "student_limit": config.student_limit,
        "language": config.language,
        "tone": config.tone,
        "anti_repeat_rules": config.anti_repeat_rules,
        "dry_run_enabled": config.dry_run_enabled,
        "created_at": config.created_at,
        "updated_at": config.updated_at,
    }
    return StreamNotificationConfigResponse(**config_dict)


@router.post("/streams/{stream_id}/config", response_model=StreamNotificationConfigResponse)
async def create_stream_notification_config(
    stream_id: int,
    config_data: StreamNotificationConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать конфигурацию уведомлений потока"""
    # Проверяем, что поток существует
    stream_query = select(Stream).where(Stream.stream_id == stream_id)
    stream_result = await db.execute(stream_query)
    stream = stream_result.scalar_one_or_none()
    
    if not stream:
        raise HTTPException(status_code=404, detail="Поток не найден")
    
    # Проверяем, что конфигурация еще не существует
    existing_config_query = select(StreamNotificationConfig).where(
        StreamNotificationConfig.stream_id == stream_id
    )
    existing_config_result = await db.execute(existing_config_query)
    existing_config = existing_config_result.scalar_one_or_none()
    
    if existing_config:
        raise HTTPException(status_code=400, detail="Конфигурация уже существует. Используйте PUT для обновления")
    
    # Обработка времени (конвертация строки в time объект)
    config_dict = config_data.model_dump()
    if config_dict.get("time"):
        from datetime import datetime as dt
        time_obj = dt.strptime(config_dict["time"], "%H:%M").time()
        config_dict["time"] = time_obj
    
    # Создаем конфигурацию
    config = StreamNotificationConfig(**config_dict)
    db.add(config)
    await db.commit()
    await db.refresh(config)
    
    # Конвертируем time в строку для ответа
    config_dict = {
        "config_id": config.config_id,
        "stream_id": config.stream_id,
        "notification_enabled": config.notification_enabled,
        "frequency": config.frequency,
        "day_of_week": config.day_of_week,
        "time": config.time.strftime("%H:%M") if config.time else None,
        "student_limit": config.student_limit,
        "language": config.language,
        "tone": config.tone,
        "anti_repeat_rules": config.anti_repeat_rules,
        "dry_run_enabled": config.dry_run_enabled,
        "created_at": config.created_at,
        "updated_at": config.updated_at,
    }
    return StreamNotificationConfigResponse(**config_dict)


@router.get("/health")
async def health_check():
    """Проверка состояния API рейтинга"""
    return {
        "status": "ok",
        "service": "rating-api",
        "timestamp": datetime.now().isoformat()
    }
