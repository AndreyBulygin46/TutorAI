# 🔄 Описание флоу n8n для системы рейтинга студентов

## 📋 Обзор флоу

### Цель флоу

Автоматизированный процесс расчета рейтинга студентов, отбора кандидатов для уведомлений и отправки персонализированных сообщений через Telegram.

### Периодичность

- **Запуск**: Еженедельно по понедельникам в 10:00 (MSK) (пока так в тесте)
- **Период анализа**: Предыдущая неделя (понедельник-воскресенье)
- **Время обработки**: 2-3 минуты

## 🎯 Шаги флоу

### 1. **Cron Trigger** ⏰

**Описание**: Запуск флоу по расписанию
**Настройки**:

- Расписание: `0 10 * * 1` (каждый понедельник в 10:00)
- Часовой пояс: Europe/Moscow
- Включен: Да

**Выходные данные**:

```json
{
  "trigger_time": "2025-01-20T10:00:00+03:00",
  "week_start": "2025-01-13",
  "week_end": "2025-01-19"
}
```

### 2. **Get Stream Configuration** 🔧

**Описание**: Получение конфигурации активных потоков
**Тип ноды**: HTTP Request
**URL**: `GET http://localhost:8000/api/v1/config/streams`
**Параметры**:

- `active_only=true`

**Обработка ошибок**:

- Retry: 3 попытки
- Timeout: 30 секунд
- Fallback: Уведомление администратора

**Выходные данные**:

```json
{
  "streams": [
    {
      "stream_id": 1,
      "name": "Октябрь 2025",
      "program_id": 1,
      "student_count": 25,
      "notification_settings": {
        "max_students_per_batch": 20,
        "language": "ru",
        "tone": "motivational"
      }
    }
  ]
}
```

### 3. **Loop Through Streams** 🔄

**Описание**: Обработка каждого потока отдельно
**Тип ноды**: Split In Batches
**Настройки**:

- Batch Size: 1
- Input: Результат предыдущего шага

### 4. **Get Students for Stream** 👥

**Описание**: Получение списка студентов потока
**Тип ноды**: HTTP Request
**URL**: `GET http://localhost:8000/api/v1/students`
**Параметры**:

- `stream_id={{ $json.stream_id }}`
- `active_only=true`
- `limit=100`

**Выходные данные**:

```json
{
  "students": [
    {
      "student_id": 1,
      "name": "Иван Петров",
      "telegram_user_id": 123456789,
      "telegram_username": "ivan_petrov"
    }
  ],
  "total": 25
}
```

### 5. **Get Weekly Facts for Each Student** 📊

**Описание**: Получение "фактов недели" для каждого студента
**Тип ноды**: HTTP Request (в цикле)
**URL**: `GET http://localhost:8000/api/v1/students/{{ $json.student_id }}/facts`
**Параметры**:

- `week_start={{ $('Cron Trigger').item.json.week_start }}`
- `week_end={{ $('Cron Trigger').item.json.week_end }}`

**Обработка ошибок**:

- Retry: 2 попытки
- Timeout: 15 секунд
- Continue on error: Да

**Выходные данные**:

```json
{
  "student_id": 1,
  "name": "Иван Петров",
  "facts": {
    "assignments": {
      "total": 5,
      "completed": 4,
      "average_grade": 85.5
    },
    "activity": {
      "messages_sent": 8,
      "last_activity": "2025-01-18T15:30:00Z"
    },
    "attendance": {
      "attendance_rate": 0.67
    }
  }
}
```

### 6. **Calculate Weekly Score** 🧮

**Описание**: Расчет рейтинга для всех студентов потока
**Тип ноды**: HTTP Request
**URL**: `POST http://localhost:8000/api/v1/rating/calculate`
**Тело запроса**:

```json
{
  "stream_id": "{{ $json.stream_id }}",
  "week_start": "{{ $('Cron Trigger').item.json.week_start }}",
  "week_end": "{{ $('Cron Trigger').item.json.week_end }}",
  "student_ids": "{{ $json.students.map(s => s.student_id) }}",
  "calculation_version": "1.0"
}
```

**Выходные данные**:

```json
{
  "calculation_id": "uuid-here",
  "results": [
    {
      "student_id": 1,
      "weekly_score": 83.2,
      "selected_for_notification": true,
      "notification_priority": "high",
      "explanation": "Студент показал высокую активность"
    }
  ]
}
```

### 7. **Filter Selected Students** 🔍

**Описание**: Фильтрация студентов, выбранных для уведомлений
**Тип ноды**: Filter
**Условие**: `{{ $json.selected_for_notification === true }}`

### 8. **Apply Anti-Repeat Rules** 🚫

**Описание**: Применение правил антиповторов
**Тип ноды**: Code
**Логика**:

```javascript
// Проверка последней рассылки
const lastNotification = await checkLastNotification(student_id);
const daysSinceLastNotification = calculateDays(lastNotification);

if (daysSinceLastNotification < 7) {
  return null; // Пропустить студента
}

return item;
```

### 9. **Limit Selection** 📏

**Описание**: Ограничение количества студентов для рассылки
**Тип ноды**: Limit
**Настройки**:

- Limit: 20 (из конфигурации потока)
- Sort by: weekly_score (по убыванию)

### 10. **Generate Personalized Messages** 💬

**Описание**: Генерация персонализированных сообщений
**Тип ноды**: HTTP Request
**URL**: `POST http://localhost:8000/api/v1/notifications/generate`
**Тело запроса**:

```json
{
  "student_id": "{{ $json.student_id }}",
  "weekly_score": "{{ $json.weekly_score }}",
  "explanation": "{{ $json.explanation }}",
  "template_type": "motivational",
  "language": "ru"
}
```

**Выходные данные**:

```json
{
  "message_text": "Привет, Иван! Твоя активность на этой неделе была отличной - 83.2 балла! Ты выполнил 4 из 5 заданий и активно участвовал в чатах. Продолжай в том же духе! 🚀",
  "message_type": "motivational",
  "personalization": {
    "name": "Иван",
    "score": 83.2,
    "achievements": ["high_activity", "good_grades"]
  }
}
```

### 11. **Send Telegram Notifications** 📱

**Описание**: Отправка уведомлений через Telegram
**Тип ноды**: Telegram
**Настройки**:

- Bot Token: `{{ $vars.TELEGRAM_BOT_TOKEN }}`
- Chat ID: `{{ $json.telegram_user_id }}`
- Message: `{{ $json.message_text }}`

**Обработка ошибок**:

- Retry: 3 попытки
- Timeout: 10 секунд
- Continue on error: Да

### 12. **Log Results** 📝

**Описание**: Логирование результатов рассылки
**Тип ноды**: HTTP Request
**URL**: `POST http://localhost:8000/api/v1/notifications/log`
**Тело запроса**:

```json
{
  "calculation_id": "{{ $('Calculate Weekly Score').item.json.calculation_id }}",
  "notification_results": "{{ $json }}",
  "sent_at": "{{ new Date().toISOString() }}"
}
```

### 13. **Send Summary to Admin** 📧

**Описание**: Отправка сводки администратору
**Тип ноды**: Email
**Настройки**:

- To: `admin@tutorai.com`
- Subject: `Weekly Score Report - {{ new Date().toLocaleDateString() }}`
- Body: `Отправлено уведомлений: {{ $json.length }} студентам`

## 🎨 Визуальная схема флоу

```
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│   Cron Trigger  │───▶│ Get Stream Config   │───▶│  Loop Streams      │
│   (Weekly)      │    │                     │    │                     │
└─────────────────┘    └──────────────────────┘    └─────────────────────┘
                                                              │
                                                              ▼
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│  Log Results   │◀───│ Send Telegram       │◀───│ Generate Messages  │
│                 │    │ Notifications        │    │                     │
└─────────────────┘    └──────────────────────┘    └─────────────────────┘
         ▲                        ▲                           ▲
         │                        │                           │
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│ Send Summary    │    │ Apply Anti-Repeat    │    │ Filter Selected     │
│ to Admin        │    │ Rules                │    │ Students            │
└─────────────────┘    └──────────────────────┘    └─────────────────────┘
         ▲                        ▲                           ▲
         │                        │                           │
┌─────────────────┐    ┌──────────────────────┐    ┌─────────────────────┐
│                 │    │ Limit Selection      │    │ Calculate Weekly    │
│                 │    │ (Max 20 students)    │    │ Score               │
└─────────────────┘    └──────────────────────┘    └─────────────────────┘
                                                              ▲
                                                              │
                                                              ▼
                                                       ┌─────────────────────┐
                                                       │ Get Students for    │
                                                       │ Stream              │
                                                       └─────────────────────┘
```

## ⚙️ Настройка n8n для работы с проектом

### 1. **Подготовка окружения**

#### Установка n8n

```bash
# Через npm
npm install n8n -g

# Через Docker
docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n
```

#### Доступ к n8n

- URL: `http://n8n.kyter.space` (указанный в задании)
- Или локально: `http://localhost:5678`

### 2. **Настройка переменных окружения**

#### В n8n Settings → Variables:

```json
{
  "TUTORAI_API_URL": "http://localhost:8000",
  "TELEGRAM_BOT_TOKEN": "your-bot-token",
  "ADMIN_EMAIL": "admin@tutorai.com",
  "DEFAULT_LANGUAGE": "ru",
  "MAX_STUDENTS_PER_BATCH": "20"
}
```

### 3. **Создание флоу**

#### Импорт флоу

1. Создать новый флоу в n8n
2. Импортировать JSON конфигурацию флоу
3. Настроить ноды под ваше окружение

#### Настройка нод

- **HTTP Request ноды**: Указать правильный URL API
- **Telegram ноды**: Добавить токен бота
- **Email ноды**: Настроить SMTP
- **Cron ноды**: Установить расписание

### 4. **Тестирование флоу**

#### Режим "сухого прогона"

```json
{
  "dry_run": true,
  "test_mode": true,
  "log_level": "debug"
}
```

#### Тестовые данные

- Использовать тестовый поток с 5-10 студентами
- Проверить все этапы флоу
- Убедиться в корректности расчетов

### 5. **Мониторинг и логирование**

#### Настройка уведомлений

- Email уведомления об ошибках
- Telegram уведомления администратору
- Логирование всех операций

#### Метрики

- Количество обработанных студентов
- Время выполнения флоу
- Количество отправленных уведомлений
- Ошибки и их частота

## 🔧 Конфигурация для разных сценариев

### Сценарий 1: Еженедельная рассылка

- **Расписание**: Каждый понедельник в 10:00
- **Период**: Предыдущая неделя
- **Лимит**: 20 студентов
- **Тон**: Мотивационный

### Сценарий 2: Ежедневная проверка

- **Расписание**: Каждый день в 9:00
- **Период**: Вчерашний день
- **Лимит**: 10 студентов
- **Тон**: Информационный

### Сценарий 3: Экстренные уведомления

- **Триггер**: Ручной запуск
- **Период**: Последние 3 дня
- **Лимит**: 50 студентов
- **Тон**: Срочный

## 🚨 Обработка ошибок

### Типы ошибок и их обработка

1. **API недоступен**: Retry + уведомление администратора
2. **Ошибка расчета**: Пропуск студента + логирование
3. **Ошибка отправки**: Retry + альтернативный канал
4. **Превышение лимитов**: Ограничение выборки

### Fallback стратегии

- Резервные каналы уведомлений
- Упрощенные сообщения при ошибках
- Автоматическое восстановление
- Ручное вмешательство при критических ошибках

## 📊 Мониторинг производительности

### Ключевые метрики

- Время выполнения флоу
- Количество обработанных студентов
- Успешность отправки уведомлений
- Точность расчетов рейтинга

### Дашборд n8n

- Статистика выполнения
- Графики производительности
- Логи ошибок
- Статус интеграций
