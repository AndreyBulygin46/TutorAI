# 🔌 План API эндпоинтов для n8n

## 📋 Обзор API для интеграции с n8n

### Базовые принципы

- **Формат ответов**: JSON
- **Аутентификация**: API ключи (планируется)
- **Версионирование**: v1
- **Кодировка**: UTF-8
- **Таймауты**: 30 секунд

## 🎯 Основные эндпоинты

### 1. **Конфигурация и настройки**

#### `GET /api/v1/config/streams`

**Описание**: Получить список активных потоков обучения
**Параметры**:

- `active_only=true` (по умолчанию)
- `program_id` (опционально)

**Ответ**:

```json
{
  "streams": [
    {
      "stream_id": 1,
      "name": "Октябрь 2025",
      "program_id": 1,
      "program_name": "Специалист по работе с системами ИИ",
      "start_date": "2025-10-01",
      "end_date": "2025-12-31",
      "student_count": 25,
      "is_active": true
    }
  ],
  "total": 1
}
```

#### `GET /api/v1/config/streams/{stream_id}`

**Описание**: Получить конфигурацию конкретного потока
**Ответ**:

```json
{
  "stream_id": 1,
  "name": "Октябрь 2025",
  "program": {
    "program_id": 1,
    "name": "Специалист по работе с системами ИИ",
    "total_hours": 144
  },
  "schedule": {
    "frequency": "weekly",
    "day_of_week": "monday",
    "time": "10:00",
    "timezone": "Europe/Moscow"
  },
  "notification_settings": {
    "max_students_per_batch": 20,
    "language": "ru",
    "tone": "motivational",
    "anti_repeat_days": 7
  }
}
```

### 2. **Студенты и их данные**

#### `GET /api/v1/students`

**Описание**: Получить список студентов с базовой информацией
**Параметры**:

- `stream_id` (обязательно)
- `active_only=true` (по умолчанию)
- `limit=100` (максимум)
- `offset=0`

**Ответ**:

```json
{
  "students": [
    {
      "student_id": 1,
      "name": "Иван Петров",
      "telegram_user_id": 123456789,
      "telegram_username": "ivan_petrov",
      "is_active": true,
      "last_login_at": "2025-01-15T10:30:00Z",
      "course_program_id": 1
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

#### `GET /api/v1/students/{student_id}/facts`

**Описание**: Получить "факты недели" для конкретного студента
**Параметры**:

- `week_start` (дата начала недели в формате YYYY-MM-DD)
- `week_end` (дата окончания недели в формате YYYY-MM-DD)

**Ответ**:

```json
{
  "student_id": 1,
  "name": "Иван Петров",
  "week_period": {
    "start": "2025-01-13",
    "end": "2025-01-19"
  },
  "facts": {
    "assignments": {
      "total": 5,
      "completed": 4,
      "on_time": 3,
      "late": 1,
      "average_grade": 85.5,
      "pending": 1
    },
    "activity": {
      "messages_sent": 8,
      "questions_asked": 5,
      "last_activity": "2025-01-18T15:30:00Z"
    },
    "attendance": {
      "scheduled_classes": 3,
      "attended": 2,
      "attendance_rate": 0.67
    },
    "engagement": {
      "study_hours": 12.5,
      "materials_viewed": 8,
      "participation_score": 75
    }
  },
  "calculated_at": "2025-01-19T23:59:59Z"
}
```

### 3. **Расчет рейтинга**

#### `POST /api/v1/rating/calculate`

**Описание**: Рассчитать рейтинг для списка студентов
**Тело запроса**:

```json
{
  "stream_id": 1,
  "week_start": "2025-01-13",
  "week_end": "2025-01-19",
  "student_ids": [1, 2, 3, 4, 5],
  "calculation_version": "1.0"
}
```

**Ответ**:

```json
{
  "calculation_id": "uuid-here",
  "stream_id": 1,
  "week_period": {
    "start": "2025-01-13",
    "end": "2025-01-19"
  },
  "results": [
    {
      "student_id": 1,
      "name": "Иван Петров",
      "weekly_score": 83.2,
      "components": {
        "assignment_score": 68.0,
        "activity_score": 100.0,
        "attendance_score": 80.0,
        "engagement_score": 100.0
      },
      "tie_breaker_factors": {
        "last_activity": "2025-01-18T15:30:00Z",
        "quality_score": 85.5,
        "deadline_compliance": 0.75
      },
      "progress_indicator": true,
      "explanation": "Студент показал высокую активность и хорошие результаты",
      "selected_for_notification": true,
      "notification_priority": "high"
    }
  ],
  "calculation_metadata": {
    "version": "1.0",
    "calculated_at": "2025-01-19T23:59:59Z",
    "total_students": 5,
    "selected_count": 3
  }
}
```

#### `GET /api/v1/rating/history`

**Описание**: Получить историю расчетов рейтинга
**Параметры**:

- `stream_id` (обязательно)
- `limit=50`
- `offset=0`
- `date_from` (опционально)
- `date_to` (опционально)

**Ответ**:

```json
{
  "calculations": [
    {
      "calculation_id": "uuid-here",
      "stream_id": 1,
      "week_period": {
        "start": "2025-01-13",
        "end": "2025-01-19"
      },
      "calculated_at": "2025-01-19T23:59:59Z",
      "total_students": 25,
      "selected_count": 8,
      "average_score": 72.5
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### 4. **Уведомления и рассылки**

#### `POST /api/v1/notifications/send`

**Описание**: Отправить уведомления выбранным студентам
**Тело запроса**:

```json
{
  "calculation_id": "uuid-here",
  "notification_type": "weekly_score",
  "student_ids": [1, 2, 3],
  "message_template": "motivational",
  "dry_run": false
}
```

**Ответ**:

```json
{
  "notification_id": "uuid-here",
  "calculation_id": "uuid-here",
  "status": "sent",
  "results": [
    {
      "student_id": 1,
      "telegram_user_id": 123456789,
      "status": "sent",
      "message_id": "telegram-message-id",
      "sent_at": "2025-01-20T10:00:00Z"
    }
  ],
  "summary": {
    "total": 3,
    "sent": 3,
    "failed": 0
  }
}
```

#### `GET /api/v1/notifications/history`

**Описание**: Получить историю уведомлений
**Параметры**:

- `stream_id` (обязательно)
- `limit=50`
- `offset=0`
- `date_from` (опционально)
- `date_to` (опционально)

### 5. **Аудит и логирование**

#### `GET /api/v1/audit/calculation/{calculation_id}`

**Описание**: Получить детальную информацию о расчете
**Ответ**:

```json
{
  "calculation_id": "uuid-here",
  "input_facts": {
    "stream_id": 1,
    "week_period": {
      "start": "2025-01-13",
      "end": "2025-01-19"
    },
    "student_count": 25
  },
  "calculation_version": "1.0",
  "formula_used": "Weekly Score = (Assignment Score × 0.4) + (Activity Score × 0.3) + (Attendance Score × 0.2) + (Engagement Score × 0.1)",
  "results": [...],
  "metadata": {
    "calculated_at": "2025-01-19T23:59:59Z",
    "processing_time_ms": 1250,
    "database_queries": 15
  }
}
```

## 🔐 Аутентификация и авторизация

### API ключи (планируется)

```http
Authorization: Bearer your-api-key-here
```

### Заголовки запросов

```http
Content-Type: application/json
Accept: application/json
User-Agent: n8n/1.0
```

## 📊 Коды ответов

### Успешные ответы

- `200 OK` - Успешный запрос
- `201 Created` - Ресурс создан
- `204 No Content` - Успешно, но без содержимого

### Ошибки клиента

- `400 Bad Request` - Неверный запрос
- `401 Unauthorized` - Не авторизован
- `403 Forbidden` - Доступ запрещен
- `404 Not Found` - Ресурс не найден
- `422 Unprocessable Entity` - Ошибка валидации

### Ошибки сервера

- `500 Internal Server Error` - Внутренняя ошибка сервера
- `502 Bad Gateway` - Ошибка шлюза
- `503 Service Unavailable` - Сервис недоступен

## 🚀 Примеры использования в n8n

### 1. Получение конфигурации потока

```javascript
// HTTP Request node
Method: GET
URL: http://localhost:8000/api/v1/config/streams/1
Headers: {
  "Content-Type": "application/json"
}
```

### 2. Получение фактов недели для студента

```javascript
// HTTP Request node
Method: GET
URL: http://localhost:8000/api/v1/students/1/facts?week_start=2025-01-13&week_end=2025-01-19
```

### 3. Расчет рейтинга

```javascript
// HTTP Request node
Method: POST
URL: http://localhost:8000/api/v1/rating/calculate
Body: {
  "stream_id": 1,
  "week_start": "2025-01-13",
  "week_end": "2025-01-19",
  "student_ids": [1, 2, 3, 4, 5]
}
```

## 🔄 Обработка ошибок

### Стандартный формат ошибки

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Неверные параметры запроса",
    "details": {
      "field": "week_start",
      "issue": "Неверный формат даты"
    }
  },
  "timestamp": "2025-01-20T10:00:00Z",
  "request_id": "uuid-here"
}
```

### Типы ошибок

- `VALIDATION_ERROR` - Ошибка валидации
- `NOT_FOUND` - Ресурс не найден
- `CALCULATION_ERROR` - Ошибка расчета
- `NOTIFICATION_ERROR` - Ошибка отправки уведомлений
- `DATABASE_ERROR` - Ошибка базы данных

## 📈 Мониторинг и метрики

### Эндпоинты для мониторинга

- `GET /api/v1/health` - Проверка состояния
- `GET /api/v1/metrics` - Метрики системы
- `GET /api/v1/status` - Статус сервисов

### Логирование

- Все запросы логируются
- Сохраняются метрики производительности
- Отслеживаются ошибки и исключения
