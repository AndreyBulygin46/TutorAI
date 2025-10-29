"""
Student service for business logic
"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.education import Student, Assignment, Message, Schedule, Stream
from app.schemas.student import (
    StudentCreate, StudentUpdate, StudentFacts, 
    StudentRating, RatingConfig
)


class StudentService:
    """Сервис для работы со студентами"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_students(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None,
        course_program_id: Optional[int] = None
    ) -> List[Student]:
        """Получить список студентов"""
        query = select(Student)
        
        if is_active is not None:
            query = query.where(Student.is_active == is_active)
        
        if course_program_id is not None:
            query = query.where(Student.course_program_id == course_program_id)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_student_by_id(self, student_id: int) -> Optional[Student]:
        """Получить студента по ID"""
        query = select(Student).where(Student.student_id == student_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_student_by_telegram_id(self, telegram_user_id: int) -> Optional[Student]:
        """Получить студента по Telegram ID"""
        query = select(Student).where(Student.telegram_user_id == telegram_user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_student(self, student_data: StudentCreate) -> Student:
        """Создать нового студента"""
        student = Student(**student_data.model_dump())
        self.db.add(student)
        await self.db.commit()
        await self.db.refresh(student)
        return student
    
    async def update_student(self, student_id: int, student_data: StudentUpdate) -> Optional[Student]:
        """Обновить студента"""
        student = await self.get_student_by_id(student_id)
        if not student:
            return None
        
        update_data = student_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(student, field, value)
        
        student.updated_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(student)
        return student
    
    async def delete_student(self, student_id: int) -> bool:
        """Удалить студента (мягкое удаление)"""
        student = await self.get_student_by_id(student_id)
        if not student:
            return False
        
        student.is_active = False
        student.updated_at = datetime.now()
        await self.db.commit()
        return True
    
    async def get_student_facts(
        self, 
        student_id: int, 
        week_start: date, 
        week_end: date
    ) -> StudentFacts:
        """Получить факты о студенте за период"""
        
        # Данные по заданиям
        assignments_query = select(
            func.count(Assignment.assignment_id).label('total'),
            func.count(Assignment.assignment_id).filter(Assignment.status == 'completed').label('completed'),
            func.count(Assignment.assignment_id).filter(
                and_(Assignment.status == 'completed', Assignment.submitted_at <= Assignment.deadline)
            ).label('on_time'),
            func.count(Assignment.assignment_id).filter(
                and_(Assignment.status == 'completed', Assignment.submitted_at > Assignment.deadline)
            ).label('late'),
            func.avg(Assignment.grade).label('average_grade')
        ).where(
            and_(
                Assignment.student_id == student_id,
                Assignment.created_at >= week_start,
                Assignment.created_at <= week_end
            )
        )
        
        assignments_result = await self.db.execute(assignments_query)
        assignments_data = assignments_result.first()
        
        # Данные по активности (сообщения)
        activity_query = select(
            func.count(Message.message_id).label('messages_sent'),
            func.count(Message.message_id).filter(Message.text_content.isnot(None)).label('questions_asked'),
            func.max(Message.created_at).label('last_activity')
        ).where(
            and_(
                Message.sender_id == student_id,
                Message.sender_type == 'user',
                Message.created_at >= week_start,
                Message.created_at <= week_end
            )
        )
        
        activity_result = await self.db.execute(activity_query)
        activity_data = activity_result.first()
        
        # Данные по посещаемости
        attendance_query = select(
            func.count(Schedule.schedule_id).label('scheduled_classes'),
            func.count(Schedule.schedule_id).filter(Schedule.is_completed.is_(True)).label('attended')
        ).where(
            and_(
                Schedule.stream_id.in_(
                    select(Stream.stream_id).join(Student.streams).where(Student.student_id == student_id)
                ),
                Schedule.scheduled_date >= week_start,
                Schedule.scheduled_date <= week_end
            )
        )
        
        attendance_result = await self.db.execute(attendance_query)
        attendance_data = attendance_result.first()
        
        # Данные по вовлеченности (упрощенная версия)
        engagement_query = select(
            func.count(Assignment.assignment_id).label('study_hours'),
            func.count(Assignment.assignment_id).label('materials_viewed'),
            func.avg(Assignment.grade).label('participation_score')
        ).where(
            and_(
                Assignment.student_id == student_id,
                Assignment.created_at >= week_start,
                Assignment.created_at <= week_end
            )
        )
        
        engagement_result = await self.db.execute(engagement_query)
        engagement_data = engagement_result.first()
        
        return StudentFacts(
            student_id=student_id,
            week_start=week_start,
            week_end=week_end,
            assignments={
                'total': assignments_data.total or 0,
                'completed': assignments_data.completed or 0,
                'on_time': assignments_data.on_time or 0,
                'late': assignments_data.late or 0,
                'average_grade': float(assignments_data.average_grade) if assignments_data.average_grade else 0.0
            },
            activity={
                'messages_sent': activity_data.messages_sent or 0,
                'questions_asked': activity_data.questions_asked or 0,
                'last_activity': activity_data.last_activity
            },
            attendance={
                'scheduled_classes': attendance_data.scheduled_classes or 0,
                'attended': attendance_data.attended or 0,
                'attendance_rate': (attendance_data.attended / attendance_data.scheduled_classes) if attendance_data.scheduled_classes else 0.0
            },
            engagement={
                'study_hours': (engagement_data.study_hours or 0) * 2,  # Примерная оценка
                'materials_viewed': engagement_data.materials_viewed or 0,
                'participation_score': float(engagement_data.participation_score) if engagement_data.participation_score else 0.0
            }
        )
    
    async def calculate_student_rating(
        self, 
        student_id: int, 
        week_start: date, 
        week_end: date,
        config: Optional[RatingConfig] = None
    ) -> StudentRating:
        """Рассчитать рейтинг студента"""
        if config is None:
            config = RatingConfig()
        
        facts = await self.get_student_facts(student_id, week_start, week_end)
        
        # Расчет компонентов рейтинга
        assignment_score = self._calculate_assignment_score(facts.assignments)
        activity_score = self._calculate_activity_score(facts.activity)
        attendance_score = self._calculate_attendance_score(facts.attendance)
        engagement_score = self._calculate_engagement_score(facts.engagement)
        
        # Итоговый рейтинг
        weekly_score = (
            assignment_score * config.assignment_weight +
            activity_score * config.activity_weight +
            attendance_score * config.attendance_weight +
            engagement_score * config.engagement_weight
        )
        
        # Определение категории
        category = self._get_rating_category(weekly_score)
        
        # Генерация рекомендаций
        recommendations = self._generate_recommendations(
            weekly_score, assignment_score, activity_score, 
            attendance_score, engagement_score, facts
        )
        
        # Генерация персонального сообщения
        personal_message = self._generate_personal_message(
            student_id, weekly_score, category, recommendations, facts
        )
        
        return StudentRating(
            student_id=student_id,
            weekly_score=round(weekly_score, 2),
            assignment_score=round(assignment_score, 2),
            activity_score=round(activity_score, 2),
            attendance_score=round(attendance_score, 2),
            engagement_score=round(engagement_score, 2),
            category=category,
            recommendations=recommendations,
            message=personal_message
        )
    
    def _calculate_assignment_score(self, assignments: Dict[str, Any]) -> float:
        """Рассчитать рейтинг по заданиям"""
        total = assignments['total']
        completed = assignments['completed']
        average_grade = assignments['average_grade']
        
        if total == 0:
            return 0.0
        
        # Базовый рейтинг по количеству выполненных заданий
        completion_rate = completed / total
        base_score = completion_rate * 80  # 80% за количество
        
        # Бонус за качество (средняя оценка)
        quality_bonus = (average_grade / 100) * 20  # 20% за качество
        
        # Штрафы за опоздания
        late_penalty = assignments['late'] * 5
        
        score = base_score + quality_bonus - late_penalty
        return max(0, min(100, score))
    
    def _calculate_activity_score(self, activity: Dict[str, Any]) -> float:
        """Рассчитать рейтинг по активности"""
        messages_sent = activity['messages_sent']
        questions_asked = activity['questions_asked']
        
        # Базовый рейтинг по количеству сообщений
        expected_messages = 5  # Ожидаемое количество сообщений в неделю
        base_score = min((messages_sent / expected_messages) * 100, 100)
        
        # Бонус за качественные вопросы
        quality_bonus = questions_asked * 3
        
        score = base_score + quality_bonus
        return max(0, min(100, score))
    
    def _calculate_attendance_score(self, attendance: Dict[str, Any]) -> float:
        """Рассчитать рейтинг по посещаемости"""
        scheduled = attendance['scheduled_classes']
        attended = attendance['attended']
        
        if scheduled == 0:
            return 100.0  # Если нет занятий, считаем идеальную посещаемость
        
        attendance_rate = attended / scheduled
        return attendance_rate * 100
    
    def _calculate_engagement_score(self, engagement: Dict[str, Any]) -> float:
        """Рассчитать рейтинг по вовлеченности"""
        study_hours = engagement['study_hours']
        materials_viewed = engagement['materials_viewed']
        participation_score = engagement['participation_score']
        
        # Ожидаемые показатели
        expected_hours = 10  # Ожидаемое количество часов в неделю
        expected_materials = 5  # Ожидаемое количество материалов
        
        hours_score = min((study_hours / expected_hours) * 50, 50)
        materials_score = min((materials_viewed / expected_materials) * 30, 30)
        participation_score = min(participation_score * 0.2, 20)
        
        return hours_score + materials_score + participation_score
    
    def _get_rating_category(self, score: float) -> str:
        """Определить категорию рейтинга"""
        if score >= 90:
            return "high"
        elif score >= 70:
            return "medium"
        elif score >= 50:
            return "low"
        else:
            return "critical"
    
    def _generate_recommendations(
        self, 
        weekly_score: float, 
        assignment_score: float, 
        activity_score: float,
        attendance_score: float, 
        engagement_score: float,
        facts: StudentFacts
    ) -> List[str]:
        """Сгенерировать рекомендации для студента"""
        recommendations = []
        
        if assignment_score < 70:
            recommendations.append("Попробуй выполнять больше заданий и сдавать их в срок")
        
        if activity_score < 70:
            recommendations.append("Будь активнее в чатах - задавай вопросы и участвуй в обсуждениях")
        
        if attendance_score < 70:
            recommendations.append("Старайся не пропускать занятия")
        
        if engagement_score < 70:
            recommendations.append("Уделяй больше времени изучению материалов курса")
        
        if weekly_score >= 90:
            recommendations.append("Отличная работа! Продолжай в том же духе!")
        elif weekly_score < 50:
            recommendations.append("Нужна помощь? Обращайся к преподавателям!")
        
        return recommendations
    
    def _generate_personal_message(
        self, 
        student_id: int, 
        weekly_score: float, 
        category: str,
        recommendations: List[str], 
        facts: StudentFacts
    ) -> str:
        """Сгенерировать персональное сообщение"""
        # Получаем имя студента (упрощенно)
        student_name = f"Студент #{student_id}"
        
        # Базовое сообщение
        message = f"Привет, {student_name}!\n\n"
        message += f"Твой рейтинг на этой неделе: {weekly_score:.1f} баллов 🎯\n\n"
        
        # Статистика
        message += "Твоя активность:\n"
        message += f"✅ Выполнено заданий: {facts.assignments['completed']}/{facts.assignments['total']}\n"
        message += f"💬 Сообщений в чате: {facts.activity['messages_sent']}\n"
        message += f"📚 Посещаемость: {facts.attendance['attendance_rate']:.1%}\n\n"
        
        # Рекомендации
        if recommendations:
            message += "Рекомендации:\n"
            for rec in recommendations[:3]:  # Максимум 3 рекомендации
                message += f"• {rec}\n"
            message += "\n"
        
        # Заключение
        if category == "high":
            message += "Продолжай в том же духе! 🚀"
        elif category == "medium":
            message += "Хорошая работа! Есть куда расти! 💪"
        elif category == "low":
            message += "Давай вместе улучшим результаты! 🤝"
        else:
            message += "Нужна помощь? Обращайся! ⚠️"
        
        message += "\n\nТвой ИИ-тьютор"
        
        return message
