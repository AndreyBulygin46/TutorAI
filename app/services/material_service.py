"""
Material service for business logic
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.education import CourseMaterial, Lesson, MaterialCategory
from app.schemas.material import (
    CourseMaterialCreate, CourseMaterialUpdate, MaterialByCategory
)


class MaterialService:
    """Сервис для работы с материалами курса"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_materials(
        self, 
        skip: int = 0, 
        limit: int = 100,
        lesson_id: Optional[int] = None,
        material_category: Optional[MaterialCategory] = None,
        is_public: Optional[bool] = None
    ) -> List[CourseMaterial]:
        """Получить список материалов курса"""
        query = select(CourseMaterial)
        
        if lesson_id is not None:
            query = query.where(CourseMaterial.lesson_id == lesson_id)
        
        if material_category is not None:
            query = query.where(CourseMaterial.material_category == material_category)
        
        if is_public is not None:
            query = query.where(CourseMaterial.is_public == is_public)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_material_by_id(self, material_id: int) -> Optional[CourseMaterial]:
        """Получить материал по ID"""
        query = select(CourseMaterial).where(CourseMaterial.material_id == material_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_material(self, material_data: CourseMaterialCreate) -> CourseMaterial:
        """Создать новый материал курса"""
        material = CourseMaterial(**material_data.model_dump())
        self.db.add(material)
        await self.db.commit()
        await self.db.refresh(material)
        return material
    
    async def update_material(
        self, 
        material_id: int, 
        material_data: CourseMaterialUpdate
    ) -> Optional[CourseMaterial]:
        """Обновить материал курса"""
        material = await self.get_material_by_id(material_id)
        if not material:
            return None
        
        update_data = material_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(material, field, value)
        
        await self.db.commit()
        await self.db.refresh(material)
        return material
    
    async def delete_material(self, material_id: int) -> bool:
        """Удалить материал курса"""
        material = await self.get_material_by_id(material_id)
        if not material:
            return False
        
        await self.db.delete(material)
        await self.db.commit()
        return True
    
    async def get_materials_by_lesson(self, lesson_id: int) -> MaterialByCategory:
        """Получить материалы урока по категориям"""
        query = select(CourseMaterial).where(CourseMaterial.lesson_id == lesson_id)
        result = await self.db.execute(query)
        materials = result.scalars().all()
        
        # Группируем по категориям
        by_category = MaterialByCategory()
        
        for material in materials:
            if material.material_category == MaterialCategory.LECTURE:
                by_category.lecture.append(material)
            elif material.material_category == MaterialCategory.ASSIGNMENT:
                by_category.assignment.append(material)
            elif material.material_category == MaterialCategory.METHODICAL:
                by_category.methodical.append(material)
        
        return by_category
    
    async def get_materials_by_category(
        self, 
        category: MaterialCategory,
        skip: int = 0,
        limit: int = 100
    ) -> List[CourseMaterial]:
        """Получить материалы по категории"""
        query = select(CourseMaterial).where(
            CourseMaterial.material_category == category
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def search_materials(
        self, 
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[CourseMaterial]:
        """Поиск материалов по названию и содержимому"""
        query = select(CourseMaterial).where(
            and_(
                CourseMaterial.title.ilike(f"%{search_term}%"),
                CourseMaterial.content.ilike(f"%{search_term}%")
            )
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_public_materials(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[CourseMaterial]:
        """Получить публичные материалы"""
        query = select(CourseMaterial).where(
            CourseMaterial.is_public == True
        ).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_material_stats(self) -> Dict[str, Any]:
        """Получить статистику по материалам"""
        # Общее количество материалов
        total_query = select(func.count(CourseMaterial.material_id))
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0
        
        # Материалы по категориям
        categories_query = select(
            CourseMaterial.material_category,
            func.count(CourseMaterial.material_id).label('count')
        ).group_by(CourseMaterial.material_category)
        
        categories_result = await self.db.execute(categories_query)
        categories = {row.material_category: row.count for row in categories_result}
        
        # Публичные материалы
        public_query = select(func.count(CourseMaterial.material_id)).where(
            CourseMaterial.is_public == True
        )
        public_result = await self.db.execute(public_query)
        public_count = public_result.scalar() or 0
        
        return {
            'total': total,
            'by_category': categories,
            'public': public_count,
            'private': total - public_count
        }
