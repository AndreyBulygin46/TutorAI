# План реализации API эндпоинтов для n8n (быстрая версия без изменений БД)

## Обзор архитектуры

### Цель API

Предоставить n8n доступ к данным TutorAI для расчета weekly-score используя только существующие таблицы базы данных.

### Особенности подхода

- **Минимальные изменения** - используются только существующие таблицы
- **Быстрый запуск** - не требует миграций БД
- **SQL-представления** - для расчета рейтинга на лету

## Эндпоинты API

### 1. Аутентификация (аналогично полной версии)

```python
POST /api/v1/auth/login
Content-Type: application/json

{
    "username": "n8n_service",
    "password": "service_password"
}
```

### 2. Получение конфигурации группы (упрощенная версия)

```python
GET /api/v1/groups/{group_id}/config
Authorization: Bearer {token}

Response:
{
    "group_id": 123,
    "group_name": "Python Advanced 2024",
    "rating_weights": {
        "academic": 0.6,
        "progress": 0.4
    },
    "schedule": {
        "frequency": "weekly",
        "day_of_week": 1
    },
    "selection_rules": {
        "sample_limit": 10,
        "min_score_threshold": 70
    }
}
```

### 3. Получение текущего рейтинга студентов (SQL-расчет на лету)

```python
GET /api/v1/groups/{group_id}/students/current-ratings
Authorization: Bearer {token}

Response:
{
    "calculated_at": "2024-01-08T10:00:00Z",
    "students": [
        {
            "student_id": 789,
            "name": "Иван Петров", 
            "telegram_user_id": 123456789,
            "current_rating": 78.5,
            "academic_score": 82.0,
            "progress_score": 72.0,
            "last_activity": "2024-01-07T15:30:00"
        }
    ]
}
```

### 4. Получение "фактов недели" для студента (упрощенная версия)

```python
GET /api/v1/students/{student_id}/weekly-facts
Authorization: Bearer {token}
Query params: period_start=2024-01-01&period_end=2024-01-07

Response:
{
    "student_id": 789,
    "period": {
        "start": "2024-01-01",
        "end": "2024-01-07"
    },
    "academic_facts": {
        "assignments_completed": 3,
        "assignments_submitted": 2,
        "average_grade": 4.2,
        "timely_submissions": 2,
        "late_submissions": 1
    },
    "progress_facts": {
        "lessons_with_assignments": 5,
        "lessons_total": 8,
        "progress_percentage": 62.5,
        "estimated_attendance": 75.0  # на основе выполненных заданий
    },
    "calculated_rating": 78.5
}
```

### 5. SQL-представление для расчета рейтинга

```sql
CREATE OR REPLACE VIEW student_current_ratings AS
WITH student_assignments AS (
    SELECT 
        a.student_id,
        a.grade,
        a.deadline,
        a.submitted_at,
        a.status,
        l.lesson_id,
        s.stream_id
    FROM assignments a
    JOIN lessons l ON a.lesson_id = l.lesson_id
    JOIN schedule s ON l.lesson_id = s.lesson_id
    WHERE a.status IN ('CHECKED', 'COMPLETED', 'SUBMITTED')
),
rating_calculations AS (
    SELECT 
        sa.student_id,
        -- Академическая успеваемость (60%)
        AVG(CASE 
            WHEN sa.status IN ('CHECKED', 'COMPLETED') THEN 
                sa.grade * 
                CASE 
                    WHEN sa.submitted_at <= sa.deadline THEN 1.0
                    WHEN sa.submitted_at <= sa.deadline + INTERVAL '7 days' THEN 0.8
                    ELSE 0.6
                END
            ELSE 0
        END) as academic_score,
      
        -- Прогресс по курсу (40%)
        (COUNT(DISTINCT sa.lesson_id) * 100.0 / 
         (SELECT COUNT(DISTINCT lesson_id) FROM schedule WHERE stream_id = sa.stream_id)
        ) as progress_percent
    FROM student_assignments sa
    GROUP BY sa.student_id, sa.stream_id
)
SELECT 
    s.student_id,
    s.name,
    s.telegram_user_id,
    rc.academic_score,
    rc.progress_percent,
    -- Итоговый рейтинг
    (rc.academic_score * 0.6) + (rc.progress_percent * 0.4) as current_rating,
    s.last_login_at as last_activity
FROM students s
JOIN rating_calculations rc ON s.student_id = rc.student_id
WHERE s.is_active = true;
```

### 6. Сохранение результатов расчета weekly-score

```python
POST /api/v1/audit/weekly-score
Authorization: Bearer {token}
Content-Type: application/json

{
    "student_id": 789,
    "period_start": "2024-01-01",
    "period_end": "2024-01-07",
    "calculated_rating": 78.5,
    "input_facts": { ... },
    "llm_enhancement": {
        "applied": true,
        "original_score": 78.5,
        "enhanced_score": 82.0,
        "explanation": "Учтены дополнительные факторы...",
        "significant_progress": false
    },
    "selection_decision": {
        "selected": true,
        "reason": "score_above_threshold"
    }
}
```

### 7. Эндпоинт для прямого SQL-запроса (опционально)

```python
POST /api/v1/query/rating
Authorization: Bearer {token}
Content-Type: application/json

{
    "student_id": 789,
    "stream_id": 123,
    "period_start": "2024-01-01",
    "period_end": "2024-01-07"
}

Response:
{
    "rating_components": {
        "academic_score": 82.0,
        "progress_percent": 62.5,
        "estimated_attendance": 75.0
    },
    "final_rating": 78.5,
    "calculation_details": "..."
}
```

## Модели данных Pydantic

```python
from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional

class SimplifiedWeeklyFacts(BaseModel):
    student_id: int
    period_start: date
    period_end: date
    academic_facts: dict
    progress_facts: dict
    calculated_rating: float

class RatingCalculation(BaseModel):
    student_id: int
    academic_score: float
    progress_percent: float
    final_rating: float
    last_activity: Optional[datetime]

class LLMEnhancement(BaseModel):
    applied: bool
    original_score: float
    enhanced_score: float
    explanation: str
    significant_progress: bool
```

## Интеграция с n8n

### Упрощенный workflow:

1. **Cron Trigger** - запуск по расписанию
2. **HTTP Request** - получение текущих рейтингов группы
3. **Function Node** - фильтрация по пороговому значению
4. **Loop** - для каждого отобранного студента:
   - Получение фактов недели
   - Вызов Anthropic для улучшения оценки
   - Генерация сообщения
   - Отправка в Telegram

### Преимущества для n8n:

- **Меньше API вызовов** - рейтинг рассчитывается одним запросом
- **Проще логика** - не нужно агрегировать данные в n8n
- **Быстрее выполнение** - SQL оптимизирован на стороне БД

## Ограничения и обходные пути

### Ограничения:

1. **Нет точной посещаемости** - используем прокси через выполненные задания
2. **Нет учета активности** - только last_login_at
3. **Фиксированные веса** - 60%/40% для всех курсов

### Обходные пути:

1. **LLM enhancement** - Anthropic может учитывать отсутствующие факторы
2. **Конфигурируемые пороги** - разные threshold для разных групп
3. **Ручная корректировка** - администратор может скорректировать отбор

## Рекомендации по реализации

1. **Создать SQL-представление** `student_current_ratings`
2. **Реализовать базовые эндпоинты** аутентификации и конфигурации
3. **Оптимизировать запросы** с индексами на часто используемых полях
4. **Добавить кэширование** рейтингов на 1-2 часа
5. **Реализовать фолбэк** на случай ошибок расчета
