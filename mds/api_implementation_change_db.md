# План реализации API эндпоинтов для n8n (полноценная версия с изменениями БД)

## Обзор архитектуры

### Цель API

Предоставить n8n доступ к данным TutorAI для расчета weekly-score и отправки персонализированных сообщений через Telegram.

### Технологический стек

- **FastAPI** - веб-фреймворк
- **SQLAlchemy 2.0** - ORM
- **PostgreSQL** - база данных
- **JWT токены** - авторизация
- **Pydantic** - валидация данных

## Эндпоинты API

### 1. Аутентификация

```python
POST /api/v1/auth/login
Content-Type: application/json

{
    "username": "n8n_service",
    "password": "service_password"
}

Response:
{
    "access_token": "jwt_token_here",
    "token_type": "bearer",
    "expires_in": 3600
}
```

### 2. Получение конфигурации группы/периода

```python
GET /api/v1/groups/{group_id}/config
Authorization: Bearer {token}

Response:
{
    "group_id": 123,
    "group_name": "Python Advanced 2024",
    "program_id": 456,
    "schedule": {
        "frequency": "weekly",
        "day_of_week": 1,  # Monday
        "time": "10:00"
    },
    "selection_rules": {
        "sample_limit": 10,
        "anti_repeat_days": 14,
        "min_score_threshold": 70
    },
    "message_settings": {
        "language": "ru",
        "tone": "supportive",
        "dry_run_enabled": true
    },
    "llm_settings": {
        "prompt_version": "v1.2",
        "model": "claude-3-sonnet",
        "temperature": 0.3
    }
}
```

### 3. Получение списка слушателей недели

```python
GET /api/v1/groups/{group_id}/students/weekly
Authorization: Bearer {token}

Response:
{
    "period_start": "2024-01-01",
    "period_end": "2024-01-07", 
    "students": [
        {
            "student_id": 789,
            "name": "Иван Петров",
            "telegram_user_id": 123456789,
            "is_active": true,
            "current_rating": 85.5
        }
    ],
    "total_count": 25
}
```

### 4. Получение "фактов недели" для студента

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
        "assignments_pending": 1,
        "average_grade": 4.2,
        "submission_timeliness": 0.9
    },
    "attendance_facts": {
        "classes_attended": 2,
        "classes_total": 3,
        "attendance_rate": 0.67
    },
    "activity_facts": {
        "logins_count": 12,
        "last_activity": "2024-01-07T15:30:00",
        "materials_viewed": 5
    },
    "progress_facts": {
        "lessons_completed": 15,
        "lessons_total": 20,
        "progress_percentage": 75
    }
}
```

### 5. Сохранение результатов расчета weekly-score

```python
POST /api/v1/audit/weekly-score
Authorization: Bearer {token}
Content-Type: application/json

{
    "student_id": 789,
    "period_start": "2024-01-01",
    "period_end": "2024-01-07",
    "input_facts": { ... },  # данные из эндпоинта 4
    "prompt_version": "v1.2",
    "llm_response": {
        "score": 82,
        "tie_breaker_attributes": ["high_activity", "good_submission_timeliness"],
        "significant_progress": true,
        "explanation": "Студент показал высокую активность..."
    },
    "selection_decision": {
        "selected": true,
        "reason": "score_above_threshold",
        "anti_repeat_check": "passed"
    },
    "calculated_at": "2024-01-08T10:00:00Z"
}

Response:
{
    "audit_id": "audit_123456",
    "status": "recorded"
}
```

### 6. Сохранение статуса отправки сообщения

```python
POST /api/v1/audit/message-status
Authorization: Bearer {token}
Content-Type: application/json

{
    "audit_id": "audit_123456",
    "message_content": "Привет, Иван! На этой неделе ты...",
    "telegram_status": {
        "sent": true,
        "message_id": 987654321,
        "sent_at": "2024-01-08T10:05:00Z",
        "error": null
    },
    "message_hash": "abc123def456"  # для анти-дубликата
}
```

### 7. Сервисные эндпоинты

```python
# Получение истории аудита
GET /api/v1/audit/history?group_id=123&period_start=2024-01-01

# Запуск сухого прогона
POST /api/v1/groups/{group_id}/dry-run

# Экспорт данных для анализа
GET /api/v1/export/ratings?format=csv
```

## Модели данных Pydantic

```python
from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional

class StudentWeeklyFacts(BaseModel):
    student_id: int
    period_start: date
    period_end: date
    academic_facts: dict
    attendance_facts: dict
    activity_facts: dict
    progress_facts: dict

class LLMScoreResponse(BaseModel):
    score: float
    tie_breaker_attributes: List[str]
    significant_progress: bool
    explanation: str

class AuditRecord(BaseModel):
    audit_id: str
    student_id: int
    period_start: date
    period_end: date
    prompt_version: str
    llm_response: LLMScoreResponse
    selection_decision: dict
    created_at: datetime
```

## Настройка авторизации

### JWT Middleware

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(token: str = Depends(security)):
    # Валидация JWT токена
    if not validate_token(token.credentials):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token
```

## Интеграция с n8n

### Пример workflow в n8n:

1. **Cron Trigger** - запуск по расписанию
2. **HTTP Request** - получение конфигурации группы
3. **HTTP Request** - получение списка студентов
4. **Loop** - для каждого студента:
   - Получение фактов недели
   - Вызов Anthropic через OpenRouter
   - Валидация JSON ответа
   - Сохранение аудита
   - Проверка анти-повторов
   - Генерация сообщения
   - Отправка в Telegram

### Обработка ошибок:

- Ретраи при временных сбоях
- Fallback ветки при ошибках LLM
- Уведомления администратору

## Рекомендации по реализации

1. **Начать с базовых эндпоинтов** (аутентификация, конфигурация)
2. **Реализовать миграции БД** для новых таблиц (посещаемость, активность)
3. **Добавить индексы** для оптимизации запросов
4. **Настроить кэширование** часто запрашиваемых данных
5. **Реализовать пагинацию** для больших наборов данных
6. **Добавить мониторинг** и логирование
