# 🌐 Запуск проекта через ngrok для глобального доступа

## 📋 Обзор

Этот файл содержит подробные инструкции по настройке проекта TutorAI с использованием ngrok для обеспечения глобального доступа к локальному серверу. Это особенно полезно для интеграции с n8n и тестирования API из внешних сервисов.

## 🚀 Быстрый старт

### 1. Установка ngrok

#### Windows
```bash
# Скачать с официального сайта
# https://ngrok.com/download

# Или через Chocolatey
choco install ngrok

# Или через Scoop
scoop install ngrok
```

#### Linux/Mac
```bash
# Через Homebrew (Mac)
brew install ngrok

# Или скачать бинарный файл
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

#### Docker
```bash
# Запуск через Docker
docker run --rm -it --net=host ngrok/ngrok:latest http 8000
```

### 2. Регистрация и настройка

#### Создание аккаунта
1. Перейти на https://ngrok.com/
2. Зарегистрироваться (бесплатно)
3. Получить authtoken из панели управления

#### Настройка authtoken
```bash
# Добавить authtoken (замените YOUR_AUTHTOKEN на ваш токен)
ngrok config add-authtoken YOUR_AUTHTOKEN
```

### 3. Запуск проекта с ngrok

#### Вариант 1: Ручной запуск
```bash
# Терминал 1: Запуск проекта
cd D:\python_rep_dev\TutorAI
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Терминал 2: Запуск ngrok
ngrok http 8000
```

#### Вариант 2: Автоматический скрипт
```bash
# Создать файл start_with_ngrok.bat (Windows)
@echo off
echo Starting TutorAI with ngrok...

REM Запуск проекта в фоне
start "TutorAI" cmd /k "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Ждем 5 секунд
timeout /t 5 /nobreak

REM Запуск ngrok
echo Starting ngrok...
ngrok http 8000

pause
```

#### Вариант 3: Docker Compose с ngrok
```yaml
# docker-compose.ngrok.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    container_name: ai_tutor_db
    environment:
      POSTGRES_USER: aitutor
      POSTGRES_PASSWORD: aitutor_dev_pass
      POSTGRES_DB: ai_tutor
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    build: .
    container_name: ai_tutor_app
    depends_on:
      - postgres
    environment:
      DATABASE_URL: postgresql+asyncpg://aitutor:aitutor_dev_pass@postgres:5432/ai_tutor
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  ngrok:
    image: ngrok/ngrok:latest
    container_name: ai_tutor_ngrok
    depends_on:
      - app
    command: ["http", "app:8000"]
    ports:
      - "4040:4040"

volumes:
  postgres_data:
```

```bash
# Запуск с ngrok
docker-compose -f docker-compose.ngrok.yml up -d
```

## 🔧 Настройка проекта для ngrok

### 1. Изменение настроек CORS

#### В файле `app/main.py` добавить:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.admin.views import setup_admin

app = FastAPI(
    title="AI Tutor API",
    version="1.0.0",
    description="Backend для AI Tutor системы"
)

# Добавить CORS middleware для ngrok
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены (только для разработки!)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Админка
admin = setup_admin(app)

@app.get("/")
def root():
    """Редирект на админку"""
    return RedirectResponse(url="/admin")

@app.get("/health")
def health_check():
    return {"status": "ok", "ngrok_enabled": True}
```

### 2. Настройка переменных окружения

#### Создать файл `.env.ngrok`:
```bash
# Настройки для ngrok
NGROK_ENABLED=true
NGROK_DOMAIN=your-custom-domain.ngrok.io
NGROK_AUTHTOKEN=your_ngrok_authtoken

# Настройки приложения
DATABASE_URL=postgresql+asyncpg://aitutor:aitutor_dev_pass@localhost:5432/ai_tutor
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Telegram настройки (если нужны)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_WEBHOOK_URL=https://your-domain.ngrok.io/webhook/telegram
```

### 3. Обновление конфигурации

#### В файле `app/core/config.py`:
```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://aitutor:aitutor_dev_pass@localhost:5432/ai_tutor"
    )
    
    # App
    PROJECT_NAME: str = "AI Tutor"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Ngrok settings
    NGROK_ENABLED: bool = os.getenv("NGROK_ENABLED", "false").lower() == "true"
    NGROK_DOMAIN: str = os.getenv("NGROK_DOMAIN", "")
    
    # Telegram settings
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_WEBHOOK_URL: str = os.getenv("TELEGRAM_WEBHOOK_URL", "")

settings = Settings()
```

## 🌐 Получение публичного URL

### 1. Запуск ngrok
```bash
# Базовый запуск
ngrok http 8000

# С кастомным доменом (требует платный план)
ngrok http 8000 --domain=your-custom-domain.ngrok.io

# С аутентификацией
ngrok http 8000 --basic-auth="username:password"
```

### 2. Получение URL
После запуска ngrok вы увидите:
```
ngrok by @inconshreveable

Session Status                online
Account                       your-email@example.com
Version                       3.x.x
Region                        United States (us)
Latency                       45ms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok.io -> http://localhost:8000
Forwarding                    http://abc123.ngrok.io -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

### 3. Использование URL
- **HTTPS URL**: `https://abc123.ngrok.io` (рекомендуется)
- **HTTP URL**: `http://abc123.ngrok.io`
- **Web Interface**: `http://127.0.0.1:4040` (мониторинг запросов)

## 🔗 Интеграция с n8n

### 1. Настройка n8n для работы с ngrok

#### В n8n Settings → Variables:
```json
{
  "TUTORAI_API_URL": "https://abc123.ngrok.io",
  "TUTORAI_API_BASE": "https://abc123.ngrok.io/api/v1",
  "TELEGRAM_BOT_TOKEN": "your-bot-token",
  "ADMIN_EMAIL": "admin@tutorai.com"
}
```

### 2. Тестирование API через ngrok

#### Проверка доступности:
```bash
# Health check
curl https://abc123.ngrok.io/health

# API документация
curl https://abc123.ngrok.io/docs

# Тестовый запрос
curl -X GET "https://abc123.ngrok.io/api/v1/students" \
  -H "Content-Type: application/json"
```

#### Через браузер:
- **Админ панель**: `https://abc123.ngrok.io/admin`
- **API документация**: `https://abc123.ngrok.io/docs`
- **ReDoc**: `https://abc123.ngrok.io/redoc`

## 📱 Настройка Telegram Webhook

### 1. Получение webhook URL
```bash
# URL для webhook
WEBHOOK_URL="https://abc123.ngrok.io/webhook/telegram"
```

### 2. Настройка webhook в Telegram
```bash
# Установка webhook
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://abc123.ngrok.io/webhook/telegram"}'

# Проверка webhook
curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getWebhookInfo"
```

### 3. Добавление webhook endpoint в FastAPI
```python
# В app/main.py добавить:
@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    """Webhook для Telegram бота"""
    data = await request.json()
    # Обработка сообщений от Telegram
    return {"status": "ok"}
```

## 🔒 Безопасность при использовании ngrok

### 1. Ограничения бесплатного плана
- **Сессия**: 8 часов максимум
- **Домен**: Случайный, меняется при перезапуске
- **Трафик**: 1GB в месяц
- **Одновременные туннели**: 1

### 2. Рекомендации по безопасности
```bash
# Использование аутентификации
ngrok http 8000 --basic-auth="username:password"

# Ограничение доступа по IP
ngrok http 8000 --allow="192.168.1.0/24"

# Использование кастомного домена (платно)
ngrok http 8000 --domain=your-secure-domain.ngrok.io
```

### 3. Настройка файрвола
```bash
# Ограничение доступа к локальному серверу
# В Windows Firewall или iptables
# Разрешить только ngrok трафик
```

## 📊 Мониторинг и отладка

### 1. Web Interface ngrok
- URL: `http://127.0.0.1:4040`
- Показывает все запросы в реальном времени
- Полезно для отладки API

### 2. Логирование
```bash
# Запуск с подробными логами
ngrok http 8000 --log=stdout --log-level=debug
```

### 3. Мониторинг производительности
```bash
# Проверка статуса
curl https://abc123.ngrok.io/health

# Проверка метрик
curl https://abc123.ngrok.io/metrics
```

## 🚀 Автоматизация запуска

### 1. Скрипт для Windows (`start_ngrok.bat`)
```batch
@echo off
echo Starting TutorAI with ngrok...

REM Проверка наличия ngrok
where ngrok >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ngrok not found! Please install ngrok first.
    pause
    exit /b 1
)

REM Запуск проекта
echo Starting TutorAI...
start "TutorAI" cmd /k "cd /d D:\python_rep_dev\TutorAI && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

REM Ждем запуска
echo Waiting for TutorAI to start...
timeout /t 10 /nobreak

REM Запуск ngrok
echo Starting ngrok...
ngrok http 8000

pause
```

### 2. Скрипт для Linux/Mac (`start_ngrok.sh`)
```bash
#!/bin/bash

echo "Starting TutorAI with ngrok..."

# Проверка наличия ngrok
if ! command -v ngrok &> /dev/null; then
    echo "ngrok not found! Please install ngrok first."
    exit 1
fi

# Запуск проекта в фоне
echo "Starting TutorAI..."
cd /path/to/TutorAI
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
TUTORAI_PID=$!

# Ждем запуска
echo "Waiting for TutorAI to start..."
sleep 10

# Запуск ngrok
echo "Starting ngrok..."
ngrok http 8000

# Остановка при завершении
kill $TUTORAI_PID
```

### 3. Makefile для удобства
```makefile
# Makefile
.PHONY: start-ngrok stop-ngrok clean

start-ngrok:
	@echo "Starting TutorAI with ngrok..."
	@python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
	@sleep 5
	@ngrok http 8000

stop-ngrok:
	@pkill -f "uvicorn app.main:app"
	@pkill -f "ngrok"

clean:
	@rm -rf __pycache__
	@rm -rf .pytest_cache
	@rm -rf *.log
```

## 🐛 Решение проблем

### 1. Проблемы с подключением
```bash
# Проверка статуса ngrok
ngrok status

# Перезапуск ngrok
pkill ngrok
ngrok http 8000
```

### 2. Проблемы с CORS
```python
# Убедиться, что CORS настроен правильно
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Проблемы с портами
```bash
# Проверка занятых портов
netstat -an | findstr :8000
netstat -an | findstr :4040

# Освобождение портов
taskkill /F /IM python.exe
taskkill /F /IM ngrok.exe
```

## 📝 Полезные команды

### Ngrok команды
```bash
# Список активных туннелей
ngrok status

# Остановка всех туннелей
ngrok stop

# Просмотр конфигурации
ngrok config check

# Обновление ngrok
ngrok update
```

### Проверка доступности
```bash
# Health check
curl -I https://abc123.ngrok.io/health

# Проверка API
curl -X GET "https://abc123.ngrok.io/api/v1/students"

# Проверка админки
curl -I https://abc123.ngrok.io/admin
```

## 🎯 Итоговые URL для использования

После настройки у вас будут доступны:

- **Главная страница**: `https://abc123.ngrok.io`
- **Админ панель**: `https://abc123.ngrok.io/admin`
- **API документация**: `https://abc123.ngrok.io/docs`
- **ReDoc**: `https://abc123.ngrok.io/redoc`
- **Health check**: `https://abc123.ngrok.io/health`
- **Web Interface ngrok**: `http://127.0.0.1:4040`

## 🔄 Обновление URL в n8n

При каждом перезапуске ngrok URL меняется. Для обновления в n8n:

1. Получить новый URL из ngrok
2. Обновить переменные в n8n Settings
3. Перезапустить флоу n8n

## 📞 Поддержка

При возникновении проблем:
1. Проверить логи ngrok: `http://127.0.0.1:4040`
2. Проверить статус проекта: `https://abc123.ngrok.io/health`
3. Проверить настройки CORS в коде
4. Убедиться, что ngrok authtoken настроен правильно
