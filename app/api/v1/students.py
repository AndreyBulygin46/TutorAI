from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.services.student_service import StudentService
from app.models.education import Student
from app.schemas.student import (
    StudentCreate, StudentUpdate, StudentResponse, StudentListResponse,
    StudentFacts, StudentRating, StudentStats, RatingConfig
)

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/", response_model=StudentListResponse)
async def get_students(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=1000, description="Количество записей для возврата"),
    is_active: Optional[bool] = Query(None, description="Фильтр по активности"),
    course_program_id: Optional[int] = Query(None, description="Фильтр по программе курса"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список студентов"""
    service = StudentService(db)
    students = await service.get_students(skip, limit, is_active, course_program_id)
    
    # Получаем общее количество для пагинации
    total_query = select(func.count(Student.student_id))
    if is_active is not None:
        total_query = total_query.where(Student.is_active == is_active)
    if course_program_id is not None:
        total_query = total_query.where(Student.course_program_id == course_program_id)
    
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    return StudentListResponse(
        students=[StudentResponse.model_validate(student) for student in students],
        total=total or 0,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить студента по ID"""
    service = StudentService(db)
    student = await service.get_student_by_id(student_id)
    
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    return StudentResponse.model_validate(student)


@router.get("/telegram/{telegram_user_id}", response_model=StudentResponse)
async def get_student_by_telegram(
    telegram_user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить студента по Telegram ID"""
    service = StudentService(db)
    student = await service.get_student_by_telegram_id(telegram_user_id)
    
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    return StudentResponse.model_validate(student)


@router.post("/", response_model=StudentResponse)
async def create_student(
    student_data: StudentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать нового студента"""
    service = StudentService(db)
    
    # Проверяем, что телефон уникален
    existing_query = select(Student).where(Student.phone == student_data.phone)
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Студент с таким телефоном уже существует")
    
    student = await service.create_student(student_data)
    return StudentResponse.model_validate(student)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить студента"""
    service = StudentService(db)
    student = await service.update_student(student_id, student_data)
    
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    return StudentResponse.model_validate(student)


@router.delete("/{student_id}")
async def delete_student(
    student_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить студента (мягкое удаление)"""
    service = StudentService(db)
    success = await service.delete_student(student_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    return {"message": "Студент успешно деактивирован"}


@router.get("/{student_id}/facts", response_model=StudentFacts)
async def get_student_facts(
    student_id: int,
    week_start: date = Query(..., description="Начало недели"),
    week_end: date = Query(..., description="Конец недели"),
    db: AsyncSession = Depends(get_db)
):
    """Получить факты о студенте за период"""
    service = StudentService(db)
    
    # Проверяем, что студент существует
    student = await service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    facts = await service.get_student_facts(student_id, week_start, week_end)
    return facts


@router.get("/{student_id}/rating", response_model=StudentRating)
async def get_student_rating(
    student_id: int,
    week_start: date = Query(..., description="Начало недели"),
    week_end: date = Query(..., description="Конец недели"),
    db: AsyncSession = Depends(get_db)
):
    """Рассчитать рейтинг студента"""
    service = StudentService(db)
    
    # Проверяем, что студент существует
    student = await service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    rating = await service.calculate_student_rating(student_id, week_start, week_end)
    return rating


@router.get("/{student_id}/stats", response_model=StudentStats)
async def get_student_stats(
    student_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить статистику студента"""
    service = StudentService(db)
    
    # Проверяем, что студент существует
    student = await service.get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")
    
    # Получаем статистику за последние 30 дней
    from datetime import timedelta
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    facts = await service.get_student_facts(student_id, start_date, end_date)
    
    return StudentStats(
        student_id=student_id,
        total_assignments=facts.assignments['total'],
        completed_assignments=facts.assignments['completed'],
        average_grade=facts.assignments['average_grade'] if facts.assignments['average_grade'] > 0 else None,
        messages_count=facts.activity['messages_sent'],
        attendance_rate=facts.attendance['attendance_rate'],
        study_hours=facts.engagement['study_hours'],
        last_activity=facts.activity['last_activity']
    )
