from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.core.database import get_db
from app.services.material_service import MaterialService
from app.models.education import CourseMaterial, MaterialCategory
from app.schemas.material import (
    CourseMaterialCreate, CourseMaterialUpdate, CourseMaterialResponse,
    CourseMaterialListResponse, MaterialByCategory
)

router = APIRouter(prefix="/materials", tags=["materials"])


@router.get("/", response_model=CourseMaterialListResponse)
async def get_materials(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=1000, description="Количество записей для возврата"),
    lesson_id: Optional[int] = Query(None, description="Фильтр по уроку"),
    material_category: Optional[MaterialCategory] = Query(None, description="Фильтр по категории"),
    is_public: Optional[bool] = Query(None, description="Фильтр по публичности"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список материалов курса"""
    service = MaterialService(db)
    materials = await service.get_materials(skip, limit, lesson_id, material_category, is_public)
    
    # Получаем общее количество для пагинации
    total_query = select(func.count(CourseMaterial.material_id))
    if lesson_id is not None:
        total_query = total_query.where(CourseMaterial.lesson_id == lesson_id)
    if material_category is not None:
        total_query = total_query.where(CourseMaterial.material_category == material_category)
    if is_public is not None:
        total_query = total_query.where(CourseMaterial.is_public == is_public)
    
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    return CourseMaterialListResponse(
        materials=[CourseMaterialResponse.model_validate(material) for material in materials],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{material_id}", response_model=CourseMaterialResponse)
async def get_material(
    material_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить материал по ID"""
    service = MaterialService(db)
    material = await service.get_material_by_id(material_id)
    
    if not material:
        raise HTTPException(status_code=404, detail="Материал не найден")
    
    return CourseMaterialResponse.model_validate(material)


@router.post("/", response_model=CourseMaterialResponse)
async def create_material(
    material_data: CourseMaterialCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать новый материал курса"""
    service = MaterialService(db)
    material = await service.create_material(material_data)
    return CourseMaterialResponse.model_validate(material)


@router.put("/{material_id}", response_model=CourseMaterialResponse)
async def update_material(
    material_id: int,
    material_data: CourseMaterialUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить материал курса"""
    service = MaterialService(db)
    material = await service.update_material(material_id, material_data)
    
    if not material:
        raise HTTPException(status_code=404, detail="Материал не найден")
    
    return CourseMaterialResponse.model_validate(material)


@router.delete("/{material_id}")
async def delete_material(
    material_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить материал курса"""
    service = MaterialService(db)
    success = await service.delete_material(material_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Материал не найден")
    
    return {"message": "Материал успешно удален"}


@router.get("/lesson/{lesson_id}/by-category", response_model=MaterialByCategory)
async def get_materials_by_lesson(
    lesson_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить материалы урока по категориям"""
    service = MaterialService(db)
    materials = await service.get_materials_by_lesson(lesson_id)
    return materials


@router.get("/category/{category}", response_model=CourseMaterialListResponse)
async def get_materials_by_category(
    category: MaterialCategory,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Получить материалы по категории"""
    service = MaterialService(db)
    materials = await service.get_materials_by_category(category, skip, limit)
    
    # Получаем общее количество
    total_query = select(func.count(CourseMaterial.material_id)).where(
        CourseMaterial.material_category == category
    )
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    return CourseMaterialListResponse(
        materials=[CourseMaterialResponse.model_validate(material) for material in materials],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/search/", response_model=CourseMaterialListResponse)
async def search_materials(
    q: str = Query(..., description="Поисковый запрос"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Поиск материалов по названию и содержимому"""
    service = MaterialService(db)
    materials = await service.search_materials(q, skip, limit)
    
    # Получаем общее количество результатов поиска
    from sqlalchemy import and_
    total_query = select(func.count(CourseMaterial.material_id)).where(
        and_(
            CourseMaterial.title.ilike(f"%{q}%"),
            CourseMaterial.content.ilike(f"%{q}%")
        )
    )
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    return CourseMaterialListResponse(
        materials=[CourseMaterialResponse.model_validate(material) for material in materials],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/public/", response_model=CourseMaterialListResponse)
async def get_public_materials(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Получить публичные материалы"""
    service = MaterialService(db)
    materials = await service.get_public_materials(skip, limit)
    
    # Получаем общее количество публичных материалов
    total_query = select(func.count(CourseMaterial.material_id)).where(
        CourseMaterial.is_public == True
    )
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    return CourseMaterialListResponse(
        materials=[CourseMaterialResponse.model_validate(material) for material in materials],
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/stats/")
async def get_material_stats(
    db: AsyncSession = Depends(get_db)
):
    """Получить статистику по материалам"""
    service = MaterialService(db)
    stats = await service.get_material_stats()
    return stats
