from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.admin.views import setup_admin
from app.api.v1 import students, materials, messages, rating

app = FastAPI(
    title="AI Tutor API",
    version="1.0.0",
    description="Backend для AI Tutor системы"
)

# CORS middleware для внешних запросов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение API роутеров
app.include_router(students.router, prefix="/api/v1")
app.include_router(materials.router, prefix="/api/v1")
app.include_router(messages.router, prefix="/api/v1")
app.include_router(rating.router, prefix="/api/v1")

# Админка
admin = setup_admin(app)


@app.get("/")
def root():
    """Редирект на админку"""
    return RedirectResponse(url="/admin")


@app.get("/health")
def health_check():
    return {"status": "ok"}