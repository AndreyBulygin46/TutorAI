#!/usr/bin/env python3
"""
АВТОМАТИЧЕСКАЯ НАСТРОЙКА AI TUTOR
Полный скрипт настройки проекта
"""
import subprocess
import time
import asyncio
import sys
import os
from pathlib import Path
from datetime import date, datetime

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import engine, Base, async_session
from app.models import education  # Важно для импорта моделей
from app.models.education import (
    CourseProgram, Student, Stream, Module, Lesson,
    CourseMaterial, Schedule, Assignment, Message, BotResponse,
    Meeting, Prompt, FAQResponse
)

def run_command(command, shell=True, timeout=300):
    """Выполнить команду и вернуть статус, stdout, stderr"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True, timeout=timeout)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print(f"⏰ Команда превысила таймаут {timeout} секунд: {command}")
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

async def create_tables():
    """Создать таблицы"""
    print("🗄️ Создаем таблицы...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print('✅ Таблицы созданы!')
        return True
    except Exception as e:
        print(f"❌ Ошибка создания таблиц: {e}")
        return False

async def seed_data():
    """Загрузить тестовые данные"""
    print("🌱 Загружаем тестовые данные...")
    try:
        async with async_session() as session:
            # Программы курсов
            programs_data = [
                {
                    "name": "Специалист по работе с системами ИИ в сфере культуры",
                    "description": "Комплексная программа обучения работе с ИИ",
                    "total_hours": 144
                }
            ]
            
            programs = []
            for program_data in programs_data:
                program = CourseProgram(**program_data)
                session.add(program)
                programs.append(program)
            
            await session.flush()
            
            # Модули
            modules_data = [
                {"name": "Введение в ИИ", "order_num": 1, "duration_hours": 15},
                {"name": "Большие языковые модели", "order_num": 2, "duration_hours": 44},
                {"name": "Диффузионные нейросети", "order_num": 3, "duration_hours": 11},
                {"name": "ИИ в исследованиях", "order_num": 4, "duration_hours": 11},
                {"name": "Виртуальные ассистенты", "order_num": 5, "duration_hours": 11}
            ]
            
            modules = []
            for module_data in modules_data:
                module = Module(
                    program_id=programs[0].program_id,
                    **module_data
                )
                session.add(module)
                modules.append(module)
            
            await session.flush()
            
            # Студенты
            students_data = [
                {"name": "Иван Петров", "phone": "+79123456789", "telegram_user_id": 123456789, "telegram_username": "ivan_petrov"},
                {"name": "Мария Сидорова", "phone": "+79123456790", "telegram_user_id": 123456790, "telegram_username": "maria_sidorova"},
                {"name": "Алексей Козлов", "phone": "+79123456791", "telegram_user_id": 123456791, "telegram_username": "alex_kozlov"},
                {"name": "Елена Волкова", "phone": "+79123456792", "telegram_user_id": 123456792, "telegram_username": "elena_volkova"},
                {"name": "Дмитрий Новиков", "phone": "+79123456793", "telegram_user_id": 123456793, "telegram_username": "dmitry_novikov"}
            ]
            
            students = []
            for student_data in students_data:
                student = Student(
                    course_program_id=programs[0].program_id,
                    **student_data
                )
                session.add(student)
                students.append(student)
            
            await session.flush()
            
            # Потоки
            streams_data = [
                {"name": "Октябрь 2025", "start_date": date(2025, 10, 1), "end_date": date(2025, 12, 31)},
                {"name": "Январь 2026", "start_date": date(2026, 1, 15), "end_date": date(2026, 3, 31)}
            ]
            
            streams = []
            for stream_data in streams_data:
                stream = Stream(
                    program_id=programs[0].program_id,
                    **stream_data
                )
                session.add(stream)
                streams.append(stream)
            
            await session.flush()
            
            # Уроки
            lessons_data = [
                {"name": "Введение в ИИ", "order_num": 1, "duration_hours": 2},
                {"name": "Основы машинного обучения", "order_num": 2, "duration_hours": 3},
                {"name": "Нейронные сети", "order_num": 3, "duration_hours": 4},
                {"name": "Глубокое обучение", "order_num": 4, "duration_hours": 5},
                {"name": "Практические применения", "order_num": 5, "duration_hours": 3}
            ]
            
            lessons = []
            for lesson_data in lessons_data:
                lesson = Lesson(
                    module_id=modules[0].module_id,
                    **lesson_data
                )
                session.add(lesson)
                lessons.append(lesson)
            
            await session.flush()
            
            # Материалы курса
            materials_data = [
                {"title": "Презентация: Введение в ИИ", "material_type": "presentation", "material_category": "lecture"},
                {"title": "Видео: Основы ML", "material_type": "video", "material_category": "lecture"},
                {"title": "Практическое задание", "material_type": "assignment", "material_category": "practice"},
                {"title": "Дополнительная литература", "material_type": "document", "material_category": "reference"}
            ]
            
            materials = []
            for material_data in materials_data:
                material = CourseMaterial(
                    lesson_id=lessons[0].lesson_id,
                    **material_data
                )
                session.add(material)
                materials.append(material)
            
            await session.flush()
            
            # Расписание
            schedules_data = [
                {"scheduled_date": datetime(2025, 10, 15, 10, 0), "is_completed": False},
                {"scheduled_date": datetime(2025, 10, 17, 14, 0), "is_completed": True},
                {"scheduled_date": datetime(2025, 10, 20, 16, 0), "is_completed": False}
            ]
            
            schedules = []
            for schedule_data in schedules_data:
                schedule = Schedule(
                    lesson_id=lessons[0].lesson_id,
                    **schedule_data
                )
                session.add(schedule)
                schedules.append(schedule)
            
            await session.flush()
            
            # Задания
            assignments_data = [
                {"name": "Домашнее задание 1", "description": "Изучить основы ИИ", "status": "completed", "deadline": datetime(2025, 10, 25, 23, 59), "grade": 85},
                {"name": "Практическая работа", "description": "Создать простую нейросеть", "status": "in_progress", "deadline": datetime(2025, 11, 5, 23, 59), "grade": None},
                {"name": "Финальный проект", "description": "Разработать ИИ-решение", "status": "pending", "deadline": datetime(2025, 12, 15, 23, 59), "grade": None}
            ]
            
            assignments = []
            for i, assignment_data in enumerate(assignments_data):
                assignment = Assignment(
                    student_id=students[i % len(students)].student_id,
                    lesson_id=lessons[i % len(lessons)].lesson_id,
                    **assignment_data,
                    submitted_at=datetime(2025, 11, 10, 15, 30, 0) if assignment_data["status"] == "completed" else None,
                    checked_at=datetime(2025, 11, 26, 10, 0, 0) if assignment_data["status"] == "completed" else None
                )
                session.add(assignment)
                assignments.append(assignment)
            
            await session.flush()
            
            # Сообщения
            messages_data = [
                {"sender_type": "student", "sender_id": students[0].student_id, "text_content": "Здравствуйте! У меня вопрос по домашнему заданию."},
                {"sender_type": "student", "sender_id": students[1].student_id, "text_content": "Можете объяснить тему нейронных сетей?"},
                {"sender_type": "student", "sender_id": students[2].student_id, "text_content": "Когда будет следующее занятие?"}
            ]
            
            messages = []
            for message_data in messages_data:
                message = Message(**message_data)
                session.add(message)
                messages.append(message)
            
            await session.flush()
            
            # Ответы бота
            bot_responses_data = [
                {"message_id": messages[0].message_id, "text_content": "Конечно! По какому именно заданию у вас вопрос?"},
                {"message_id": messages[1].message_id, "text_content": "Нейронные сети - это вычислительные модели, вдохновленные биологическими нейронными сетями."},
                {"message_id": messages[2].message_id, "text_content": "Следующее занятие состоится 20 октября в 16:00."}
            ]
            
            for bot_response_data in bot_responses_data:
                bot_response = BotResponse(**bot_response_data)
                session.add(bot_response)
            
            await session.commit()
            print("✅ Тестовые данные загружены успешно!")
            print(f"📊 Создано:")
            print(f"  - Программ курсов: {len(programs)}")
            print(f"  - Модулей: {len(modules)}")
            print(f"  - Студентов: {len(students)}")
            print(f"  - Потоков: {len(streams)}")
            print(f"  - Уроков: {len(lessons)}")
            print(f"  - Материалов: {len(materials)}")
            print(f"  - Расписаний: {len(schedules)}")
            print(f"  - Заданий: {len(assignments)}")
            print(f"  - Сообщений: {len(messages)}")
            print(f"  - Ответов бота: {len(bot_responses_data)}")
            return True
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚀 АВТОМАТИЧЕСКАЯ НАСТРОЙКА AI TUTOR")
    print("=" * 50)
    
    # 1. Остановить все и очистить
    print("🧹 Очищаем старые контейнеры...")
    run_command("docker-compose down --volumes")
    run_command("docker system prune -f")
    
    # 2. Запустить все через docker-compose
    print("🐳 Запускаем все контейнеры...")
    success, stdout, error = run_command("docker-compose up -d", timeout=600)  # 10 минут на запуск
    if not success:
        print(f"❌ Ошибка запуска контейнеров: {error}")
        return False
    
    # 3. Ждать запуска
    print("⏳ Ждем запуска контейнеров...")
    time.sleep(30)
    print("✅ Контейнеры запущены!")
    
    # 4. Создать таблицы через Docker
    print("🗄️ Создаем таблицы через Docker...")
    success, output, error = run_command("docker exec ai_tutor_app python scripts/create_tables.py", timeout=60)
    if not success:
        print(f"❌ Ошибка создания таблиц: {error}")
        return False
    print("✅ Таблицы созданы!")
    
    # 5. Загрузить тестовые данные через Docker
    print("🌱 Загружаем тестовые данные через Docker...")
    success, output, error = run_command("docker exec ai_tutor_app python scripts/seed_data.py", timeout=120)
    if not success:
        print(f"❌ Ошибка загрузки данных: {error}")
        return False
    print("✅ Данные загружены!")
    
    print("\n" + "=" * 50)
    print("🎉 НАСТРОЙКА ЗАВЕРШЕНА!")
    print("📋 Доступные URL:")
    print("  - Админ панель: http://localhost:8000/admin")
    print("  - API документация: http://localhost:8000/docs")
    print("  - Главная страница: http://localhost:8000 (редирект на админку)")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
