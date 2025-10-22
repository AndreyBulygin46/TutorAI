#!/usr/bin/env python3
"""
Скрипт для загрузки тестовых данных в базу
"""
import asyncio
import sys
import os
from datetime import date, time, datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def seed_data():
    """Загрузка тестовых данных"""
    try:
        from app.core.database import async_session, engine
        from app.models.education import (
            CourseProgram, Student, Stream, Module, Lesson,
            CourseMaterial, Schedule, Assignment, Message, BotResponse,
            Meeting, Prompt, FAQResponse
        )
        from sqlalchemy.ext.asyncio import AsyncSession
        import random
        
        print("🌱 Загружаем тестовые данные...")
        
        async with async_session() as session:
            # Создаем программы курсов
            programs_data = [
                {
                    "name": "Специалист по работе с системами ИИ в сфере культуры",
                    "description": "Комплексная программа обучения работе с ИИ",
                    "total_hours": 144
                },
                {
                    "name": "Основы машинного обучения",
                    "description": "Базовый курс по ML для начинающих",
                    "total_hours": 72
                },
                {
                    "name": "Продвинутая аналитика данных",
                    "description": "Углубленный курс по анализу данных",
                    "total_hours": 120
                }
            ]
            
            programs = []
            for program_data in programs_data:
                program = CourseProgram(**program_data)
                session.add(program)
                programs.append(program)
            
            await session.flush()
            
            # Создаем модули для первой программы
            modules_data = [
                {"name": "Введение в ИИ", "order_num": 1, "duration_hours": 15, "lecture_hours": 8, "practice_hours": 5, "independent_hours": 2},
                {"name": "Большие языковые модели", "order_num": 2, "duration_hours": 44, "lecture_hours": 20, "practice_hours": 20, "independent_hours": 4},
                {"name": "Диффузионные нейросети", "order_num": 3, "duration_hours": 11, "lecture_hours": 6, "practice_hours": 4, "independent_hours": 1},
                {"name": "ИИ в исследованиях", "order_num": 4, "duration_hours": 11, "lecture_hours": 5, "practice_hours": 4, "independent_hours": 2},
                {"name": "Виртуальные ассистенты", "order_num": 5, "duration_hours": 11, "lecture_hours": 4, "practice_hours": 5, "independent_hours": 2}
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
            
            # Создаем уроки для первого модуля
            lessons_data = [
                {"name": "История развития ИИ", "order_num": 1, "duration_hours": 2},
                {"name": "Основные концепции машинного обучения", "order_num": 2, "duration_hours": 3},
                {"name": "Типы нейронных сетей", "order_num": 3, "duration_hours": 2},
                {"name": "Практическое применение ИИ", "order_num": 4, "duration_hours": 3}
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
            
            # Создаем студентов
            students_data = [
                {"phone": "+79123456789", "name": "Иван Петров", "telegram_user_id": 123456789, "telegram_username": "ivan_petrov"},
                {"phone": "+79123456790", "name": "Мария Сидорова", "telegram_user_id": 123456790, "telegram_username": "maria_sidorova"},
                {"phone": "+79123456791", "name": "Алексей Козлов", "telegram_user_id": 123456791, "telegram_username": "alex_kozlov"},
                {"phone": "+79123456792", "name": "Елена Волкова", "telegram_user_id": 123456792, "telegram_username": "elena_volkova"},
                {"phone": "+79123456793", "name": "Дмитрий Новиков", "telegram_user_id": 123456793, "telegram_username": "dmitry_novikov"}
            ]
            
            students = []
            for i, student_data in enumerate(students_data):
                student = Student(
                    **student_data,
                    is_active=True,
                    course_program_id=programs[i % len(programs)].program_id
                )
                session.add(student)
                students.append(student)
            
            await session.flush()
            
            # Создаем потоки
            streams_data = [
                {"name": "Октябрь 2025", "start_date": date(2025, 10, 1), "end_date": date(2025, 12, 31)},
                {"name": "Январь 2026", "start_date": date(2026, 1, 15), "end_date": date(2026, 4, 15)},
                {"name": "Май 2026", "start_date": date(2026, 5, 1), "end_date": date(2026, 8, 31)}
            ]
            
            streams = []
            for i, stream_data in enumerate(streams_data):
                stream = Stream(
                    program_id=programs[i % len(programs)].program_id,
                    **stream_data
                )
                session.add(stream)
                streams.append(stream)
            
            await session.flush()
            
            # Создаем материалы курса
            materials_data = [
                {"title": "Введение в ИИ - Лекция", "content": "Основные понятия и история развития", "material_type": "PDF", "material_category": "LECTURE", "is_public": True},
                {"title": "Практическое задание 1", "content": "Создание простой нейросети", "material_type": "JUPYTER", "material_category": "ASSIGNMENT", "is_public": False},
                {"title": "Методические рекомендации", "content": "Как изучать ИИ эффективно", "material_type": "DOC", "material_category": "METHODICAL", "is_public": True}
            ]
            
            for i, material_data in enumerate(materials_data):
                material = CourseMaterial(
                    lesson_id=lessons[i % len(lessons)].lesson_id,
                    **material_data
                )
                session.add(material)
            
            await session.flush()
            
            # Создаем встречи
            meetings_data = [
                {"meeting_type": "LECTURE", "meeting_date": date(2025, 10, 15), "start_time": time(10, 0), "end_time": time(12, 0), "description": "Лекция по основам ИИ"},
                {"meeting_type": "PRACTICE", "meeting_date": date(2025, 10, 17), "start_time": time(14, 0), "end_time": time(16, 0), "description": "Практическое занятие"},
                {"meeting_type": "INDEPENDENT", "meeting_date": date(2025, 10, 20), "description": "Самостоятельная работа"}
            ]
            
            for i, meeting_data in enumerate(meetings_data):
                meeting = Meeting(
                    stream_id=streams[0].stream_id,
                    lesson_id=lessons[i % len(lessons)].lesson_id,
                    **meeting_data
                )
                session.add(meeting)
            
            await session.flush()
            
            # Создаем расписание
            for i in range(10):
                schedule = Schedule(
                    stream_id=streams[0].stream_id,
                    lesson_id=lessons[i % len(lessons)].lesson_id,
                    scheduled_date=date(2025, 10, 15 + i),
                    is_completed=random.choice([True, False])
                )
                session.add(schedule)
            
            await session.flush()
            
            # Создаем задания
            assignments_data = [
                {"name": "Анализ датасета", "description": "Проанализировать предоставленный датасет", "status": "PENDING", "deadline": date(2025, 11, 1)},
                {"name": "Создание модели", "description": "Обучить модель классификации", "status": "SUBMITTED", "deadline": date(2025, 11, 15), "submitted_at": datetime(2025, 11, 10, 15, 30, 0)},
                {"name": "Финальный проект", "description": "Разработать ИИ-решение для культуры", "status": "COMPLETED", "deadline": date(2025, 12, 1), "submitted_at": datetime(2025, 11, 25, 12, 0, 0), "checked_at": datetime(2025, 11, 26, 10, 0, 0), "feedback": "Отличная работа!", "grade": 95}
            ]
            
            for i, assignment_data in enumerate(assignments_data):
                assignment = Assignment(
                    student_id=students[i % len(students)].student_id,
                    lesson_id=lessons[i % len(lessons)].lesson_id,
                    **assignment_data
                )
                session.add(assignment)
            
            await session.flush()
            
            # Создаем сообщения и ответы бота
            messages_data = [
                {"text_content": "Привет! Расскажи про ИИ в культуре", "sender_type": "user"},
                {"text_content": "Как работает машинное обучение?", "sender_type": "user"},
                {"text_content": "Можете объяснить нейронные сети?", "sender_type": "user"},
                {"text_content": "Какие есть практические применения ИИ?", "sender_type": "user"},
                {"text_content": "Как начать изучать ИИ с нуля?", "sender_type": "user"}
            ]
            
            bot_responses = [
                "Привет! ИИ в культуре - это увлекательная область, которая включает создание музыки, живописи, литературы с помощью алгоритмов.",
                "Машинное обучение - это процесс, при котором компьютер учится на данных без явного программирования каждого шага.",
                "Нейронные сети - это вычислительные системы, вдохновленные биологическими нейронными сетями мозга.",
                "Практические применения ИИ включают: распознавание изображений, обработку естественного языка, рекомендательные системы.",
                "Для изучения ИИ с нуля рекомендую начать с основ математики, программирования на Python и изучения алгоритмов."
            ]
            
            for i, message_data in enumerate(messages_data):
                message = Message(
                    chat_id=123456789 + i,
                    sender_id=students[i % len(students)].student_id,
                    **message_data
                )
                session.add(message)
                await session.flush()
                
                # Создаем ответ бота
                bot_response = BotResponse(
                    message_id=message.message_id,
                    text_content=bot_responses[i % len(bot_responses)]
                )
                session.add(bot_response)
            
            await session.flush()
            
            # Создаем промпты
            prompts_data = [
                {"prompt_type": "QUESTION_CLASSIFIER", "prompt_text": "Классифицируй вопрос по категориям: технический, общий, практический", "description": "Для классификации вопросов студентов"},
                {"prompt_type": "FAQ_RESPONSE", "prompt_text": "Ответь на часто задаваемый вопрос о ИИ", "description": "Для ответов на FAQ"},
                {"prompt_type": "MATERIAL_RESPONSE", "prompt_text": "Объясни учебный материал простыми словами", "description": "Для объяснения материалов"}
            ]
            
            for prompt_data in prompts_data:
                prompt = Prompt(**prompt_data)
                session.add(prompt)
            
            await session.flush()
            
            # Создаем FAQ ответы
            faq_data = [
                {"category": "Технические", "question": "Что такое машинное обучение?", "answer_text": "Машинное обучение - это подраздел ИИ, который позволяет компьютерам учиться на данных."},
                {"category": "Практические", "question": "Где применяется ИИ?", "answer_text": "ИИ применяется в медицине, финансах, транспорте, образовании и многих других областях."},
                {"category": "Обучение", "question": "С чего начать изучение ИИ?", "answer_text": "Начните с основ математики, программирования и изучения алгоритмов."}
            ]
            
            for faq_item in faq_data:
                faq = FAQResponse(**faq_item)
                session.add(faq)
            
            await session.commit()
            print("✅ Тестовые данные загружены успешно!")
            print(f"📊 Создано:")
            print(f"  - Программ курсов: {len(programs)}")
            print(f"  - Модулей: {len(modules)}")
            print(f"  - Уроков: {len(lessons)}")
            print(f"  - Студентов: {len(students)}")
            print(f"  - Потоков: {len(streams)}")
            print(f"  - Материалов: {len(materials_data)}")
            print(f"  - Встреч: {len(meetings_data)}")
            print(f"  - Заданий: {len(assignments_data)}")
            print(f"  - Сообщений: {len(messages_data)}")
            print(f"  - Промптов: {len(prompts_data)}")
            print(f"  - FAQ: {len(faq_data)}")
            
    except Exception as e:
        print(f"❌ Ошибка загрузки данных: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(seed_data())