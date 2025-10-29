"""
Pydantic schemas for Course Material API
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.education import MaterialCategory


class CourseMaterialBase(BaseModel):
    """Базовая схема материала курса"""
    title: str = Field(..., min_length=1, max_length=150, description="Название материала")
    content: Optional[str] = Field(None, description="Содержимое материала")
    file_path: Optional[str] = Field(None, max_length=255, description="Путь к файлу")
    material_type: Optional[str] = Field(None, max_length=50, description="Тип материала")
    material_category: MaterialCategory = Field(..., description="Категория материала")
    is_public: bool = Field(False, description="Публичный ли материал")


class CourseMaterialCreate(CourseMaterialBase):
    """Схема для создания материала курса"""
    lesson_id: int = Field(..., description="ID урока")


class CourseMaterialUpdate(BaseModel):
    """Схема для обновления материала курса"""
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    content: Optional[str] = None
    file_path: Optional[str] = Field(None, max_length=255)
    material_type: Optional[str] = Field(None, max_length=50)
    material_category: Optional[MaterialCategory] = None
    is_public: Optional[bool] = None


class CourseMaterialResponse(CourseMaterialBase):
    """Схема ответа для материала курса"""
    model_config = ConfigDict(from_attributes=True)
    
    material_id: int = Field(..., description="ID материала")
    lesson_id: int = Field(..., description="ID урока")
    created_at: datetime = Field(..., description="Дата создания")


class CourseMaterialListResponse(BaseModel):
    """Схема для списка материалов курса"""
    materials: List[CourseMaterialResponse]
    total: int = Field(..., description="Общее количество материалов")
    page: int = Field(..., description="Текущая страница")
    size: int = Field(..., description="Размер страницы")


class MaterialByCategory(BaseModel):
    """Материалы по категориям"""
    lecture: List[CourseMaterialResponse] = Field(default_factory=list)
    assignment: List[CourseMaterialResponse] = Field(default_factory=list)
    methodical: List[CourseMaterialResponse] = Field(default_factory=list)
