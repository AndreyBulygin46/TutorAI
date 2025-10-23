# ⚙️ Шаблон конфигурации группы/периода/программы

## 📋 Обзор конфигурации

### Назначение
Конфигурационные файлы для настройки параметров расчета рейтинга, правил отбора студентов и параметров рассылки уведомлений для каждого потока обучения.

### Формат
- **JSON** - основной формат
- **YAML** - альтернативный формат
- **Переменные окружения** - для чувствительных данных

## 🎯 Основной шаблон конфигурации

### `config/streams/{stream_id}.json`

```json
{
  "stream_id": 1,
  "name": "Октябрь 2025",
  "program_id": 1,
  "program_name": "Специалист по работе с системами ИИ в сфере культуры",
  
  "schedule": {
    "frequency": "weekly",
    "day_of_week": "monday",
    "time": "10:00",
    "timezone": "Europe/Moscow",
    "enabled": true
  },
  
  "notification_settings": {
    "max_students_per_batch": 20,
    "min_score_threshold": 50,
    "language": "ru",
    "tone": "motivational",
    "anti_repeat_days": 7,
    "dry_run_enabled": false
  },
  
  "rating_calculation": {
    "version": "1.0",
    "formula": {
      "assignment_weight": 0.4,
      "activity_weight": 0.3,
      "attendance_weight": 0.2,
      "engagement_weight": 0.1
    },
    "bonuses": {
      "on_time_submission": 10,
      "high_activity": 5,
      "quality_questions": 3,
      "group_participation": 2
    },
    "penalties": {
      "late_submission_per_day": -5,
      "low_attendance": -10,
      "inactivity": -15
    }
  },
  
  "selection_criteria": {
    "min_weekly_score": 60,
    "max_students_per_notification": 20,
    "priority_factors": [
      "weekly_score",
      "last_activity",
      "quality_score",
      "deadline_compliance"
    ],
    "tie_breaker_rules": {
      "last_activity_weight": 0.3,
      "quality_score_weight": 0.4,
      "deadline_compliance_weight": 0.3
    }
  },
  
  "message_templates": {
    "motivational": {
      "high_score": "Отличная работа! Твой рейтинг {score} баллов показывает высокую активность. Продолжай в том же духе! 🚀",
      "medium_score": "Хорошая работа! Твой рейтинг {score} баллов. Есть куда расти - попробуй быть активнее в чатах! 💪",
      "low_score": "Твой рейтинг {score} баллов. Давай вместе улучшим результаты! Я готов помочь! 🤝"
    },
    "informational": {
      "schedule": "Напоминание: следующее занятие {date} в {time}. Не забудь подготовиться! 📅",
      "deadline": "Внимание! Дедлайн по заданию '{assignment}' - {deadline}. Время еще есть! ⏰",
      "progress": "Твоя активность за неделю: {assignments} заданий, {messages} сообщений, {attendance}% посещаемость"
    },
    "urgent": {
      "low_activity": "⚠️ Низкая активность! Твой рейтинг {score} баллов. Нужна помощь? Обращайся!",
      "missed_deadline": "🚨 Просрочен дедлайн по заданию '{assignment}'. Срочно сдавай!",
      "attendance_warning": "📢 Низкая посещаемость {attendance}%. Посещай занятия регулярно!"
    }
  },
  
  "anti_repeat_rules": {
    "enabled": true,
    "min_interval_days": 7,
    "max_notifications_per_week": 2,
    "message_variation": true,
    "content_rotation": [
      "motivational",
      "informational", 
      "progress_update"
    ]
  },
  
  "telegram_settings": {
    "bot_token": "${TELEGRAM_BOT_TOKEN}",
    "chat_id_field": "telegram_user_id",
    "message_format": "markdown",
    "parse_mode": "HTML",
    "disable_web_page_preview": true,
    "disable_notification": false
  },
  
  "monitoring": {
    "log_level": "INFO",
    "save_calculations": true,
    "save_notifications": true,
    "admin_notifications": {
      "enabled": true,
      "email": "admin@tutorai.com",
      "telegram_chat_id": "123456789"
    }
  },
  
  "advanced_settings": {
    "calculation_timeout": 300,
    "notification_timeout": 30,
    "retry_attempts": 3,
    "batch_processing": true,
    "parallel_processing": false,
    "cache_enabled": true,
    "cache_ttl": 3600
  }
}
```

## 📊 Специализированные конфигурации

### Конфигурация для разных типов программ

#### `config/programs/ai_culture.json`
```json
{
  "program_type": "ai_culture",
  "specific_settings": {
    "assignment_types": ["practical", "research", "creative"],
    "activity_indicators": ["chat_participation", "material_engagement", "peer_interaction"],
    "bonus_criteria": {
      "creative_assignments": 15,
      "research_quality": 10,
      "peer_help": 5
    }
  }
}
```

#### `config/programs/basic_ml.json`
```json
{
  "program_type": "basic_ml",
  "specific_settings": {
    "assignment_types": ["coding", "theory", "practice"],
    "activity_indicators": ["code_submissions", "forum_participation", "help_requests"],
    "bonus_criteria": {
      "code_quality": 20,
      "theory_understanding": 10,
      "peer_support": 8
    }
  }
}
```

### Конфигурация для разных периодов

#### `config/periods/beginning.json`
```json
{
  "period_type": "beginning",
  "description": "Первые 4 недели обучения",
  "adjustments": {
    "score_multiplier": 1.2,
    "bonus_for_new_students": 10,
    "lenient_deadlines": true,
    "extra_guidance": true
  }
}
```

#### `config/periods/midterm.json`
```json
{
  "period_type": "midterm",
  "description": "Середина курса (5-8 неделя)",
  "adjustments": {
    "score_multiplier": 1.0,
    "strict_deadlines": true,
    "quality_focus": true,
    "peer_comparison": true
  }
}
```

#### `config/periods/final.json`
```json
{
  "period_type": "final",
  "description": "Финальные недели (9-12 неделя)",
  "adjustments": {
    "score_multiplier": 0.9,
    "project_focus": true,
    "final_push_bonus": 15,
    "graduation_preparation": true
  }
}
```

## 🔧 Конфигурация для n8n

### `config/n8n/workflow_settings.json`
```json
{
  "workflow_id": "weekly_score_calculation",
  "version": "1.0",
  "enabled": true,
  
  "triggers": {
    "cron": {
      "schedule": "0 10 * * 1",
      "timezone": "Europe/Moscow",
      "enabled": true
    },
    "manual": {
      "enabled": true,
      "admin_only": true
    }
  },
  
  "api_settings": {
    "base_url": "http://localhost:8000",
    "timeout": 30,
    "retry_attempts": 3,
    "rate_limit": {
      "requests_per_minute": 60,
      "burst_limit": 10
    }
  },
  
  "processing_settings": {
    "batch_size": 20,
    "parallel_processing": false,
    "error_handling": "continue",
    "logging_level": "INFO"
  },
  
  "notification_settings": {
    "telegram": {
      "enabled": true,
      "bot_token": "${TELEGRAM_BOT_TOKEN}",
      "rate_limit": 30
    },
    "email": {
      "enabled": true,
      "smtp_server": "${SMTP_SERVER}",
      "smtp_port": 587,
      "username": "${SMTP_USERNAME}",
      "password": "${SMTP_PASSWORD}"
    }
  }
}
```

## 🌍 Локализация и языки

### `config/languages/ru.json`
```json
{
  "language": "ru",
  "messages": {
    "high_score": "Отличная работа! Твой рейтинг {score} баллов показывает высокую активность. Продолжай в том же духе! 🚀",
    "medium_score": "Хорошая работа! Твой рейтинг {score} баллов. Есть куда расти - попробуй быть активнее в чатах! 💪",
    "low_score": "Твой рейтинг {score} баллов. Давай вместе улучшим результаты! Я готов помочь! 🤝",
    "schedule_reminder": "Напоминание: следующее занятие {date} в {time}. Не забудь подготовиться! 📅",
    "deadline_warning": "Внимание! Дедлайн по заданию '{assignment}' - {deadline}. Время еще есть! ⏰"
  },
  "templates": {
    "greeting": "Привет, {name}!",
    "closing": "Удачи в учебе! 📚",
    "signature": "Твой ИИ-тьютор"
  }
}
```

### `config/languages/en.json`
```json
{
  "language": "en",
  "messages": {
    "high_score": "Excellent work! Your score of {score} points shows high activity. Keep it up! 🚀",
    "medium_score": "Good work! Your score of {score} points. There's room to grow - try to be more active in chats! 💪",
    "low_score": "Your score is {score} points. Let's improve the results together! I'm ready to help! 🤝",
    "schedule_reminder": "Reminder: next class on {date} at {time}. Don't forget to prepare! 📅",
    "deadline_warning": "Attention! Deadline for assignment '{assignment}' - {deadline}. There's still time! ⏰"
  },
  "templates": {
    "greeting": "Hello, {name}!",
    "closing": "Good luck with your studies! 📚",
    "signature": "Your AI Tutor"
  }
}
```

## 🔒 Безопасность и секреты

### `config/secrets/.env`
```bash
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Email Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ai_tutor

# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key

# Admin Settings
ADMIN_EMAIL=admin@tutorai.com
ADMIN_TELEGRAM_ID=123456789
```

### `config/secrets/secrets.json`
```json
{
  "telegram": {
    "bot_token": "${TELEGRAM_BOT_TOKEN}",
    "webhook_url": "${WEBHOOK_URL}"
  },
  "email": {
    "smtp_server": "${SMTP_SERVER}",
    "smtp_port": "${SMTP_PORT}",
    "username": "${SMTP_USERNAME}",
    "password": "${SMTP_PASSWORD}"
  },
  "ai_services": {
    "openai_api_key": "${OPENAI_API_KEY}",
    "anthropic_api_key": "${ANTHROPIC_API_KEY}"
  }
}
```

## 📈 Мониторинг и метрики

### `config/monitoring/metrics.json`
```json
{
  "enabled": true,
  "collection_interval": 300,
  "metrics": {
    "calculation_time": true,
    "notification_success_rate": true,
    "student_engagement": true,
    "error_rate": true
  },
  "alerts": {
    "high_error_rate": {
      "threshold": 0.1,
      "notification": "email"
    },
    "low_engagement": {
      "threshold": 0.3,
      "notification": "telegram"
    },
    "calculation_timeout": {
      "threshold": 300,
      "notification": "both"
    }
  }
}
```

## 🚀 Развертывание конфигурации

### Автоматическое развертывание
```bash
# Копирование конфигураций
cp config/streams/*.json /app/config/streams/
cp config/languages/*.json /app/config/languages/
cp config/secrets/.env /app/.env

# Применение конфигурации
python scripts/apply_config.py --stream-id 1
```

### Валидация конфигурации
```bash
# Проверка синтаксиса
python scripts/validate_config.py config/streams/1.json

# Проверка всех конфигураций
python scripts/validate_all_configs.py
```

### Обновление конфигурации
```bash
# Hot reload (без перезапуска)
curl -X POST http://localhost:8000/api/v1/config/reload

# Применение изменений
python scripts/update_config.py --stream-id 1 --config-file new_config.json
```

## 📝 Документация конфигурации

### Схема валидации
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["stream_id", "name", "schedule", "notification_settings"],
  "properties": {
    "stream_id": {"type": "integer"},
    "name": {"type": "string"},
    "schedule": {
      "type": "object",
      "required": ["frequency", "day_of_week", "time"],
      "properties": {
        "frequency": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
        "day_of_week": {"type": "string"},
        "time": {"type": "string", "pattern": "^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$"},
        "timezone": {"type": "string"},
        "enabled": {"type": "boolean"}
      }
    }
  }
}
```

### Примеры использования
```python
# Загрузка конфигурации
import json
with open('config/streams/1.json', 'r') as f:
    config = json.load(f)

# Применение настроек
max_students = config['notification_settings']['max_students_per_batch']
language = config['notification_settings']['language']
tone = config['notification_settings']['tone']
```
