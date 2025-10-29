from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional

from app.core.database import get_db
from app.services.message_service import MessageService
from app.models.education import Message, SenderType
from app.schemas.message import (
    MessageCreate, MessageResponse, BotResponseCreate, BotResponseResponse,
    MessageWithResponse, MessageListResponse, ChatStats
)

router = APIRouter(prefix="/messages", tags=["messages"])


@router.get("/", response_model=MessageListResponse)
async def get_messages(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=1000, description="Количество записей для возврата"),
    chat_id: Optional[int] = Query(None, description="Фильтр по чату"),
    sender_type: Optional[SenderType] = Query(None, description="Фильтр по типу отправителя"),
    sender_id: Optional[int] = Query(None, description="Фильтр по ID отправителя"),
    db: AsyncSession = Depends(get_db)
):
    """Получить список сообщений с ответами бота"""
    service = MessageService(db)
    messages = await service.get_messages(skip, limit, chat_id, sender_type, sender_id)
    
    # Получаем общее количество для пагинации
    total_query = select(func.count(Message.message_id))
    if chat_id is not None:
        total_query = total_query.where(Message.chat_id == chat_id)
    if sender_type is not None:
        total_query = total_query.where(Message.sender_type == sender_type)
    if sender_id is not None:
        total_query = total_query.where(Message.sender_id == sender_id)
    
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    return MessageListResponse(
        messages=messages,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/{message_id}", response_model=MessageWithResponse)
async def get_message(
    message_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить сообщение по ID с ответами бота"""
    service = MessageService(db)
    message = await service.get_message_by_id(message_id)
    
    if not message:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    
    return message


@router.post("/", response_model=MessageResponse)
async def create_message(
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать новое сообщение"""
    service = MessageService(db)
    message = await service.create_message(message_data)
    return MessageResponse.model_validate(message)


@router.post("/{message_id}/bot-response", response_model=BotResponseResponse)
async def create_bot_response(
    message_id: int,
    response_data: BotResponseCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать ответ бота на сообщение"""
    service = MessageService(db)
    
    # Проверяем, что сообщение существует
    message = await service.get_message_by_id(message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    
    # Устанавливаем message_id из URL
    response_data.message_id = message_id
    
    response = await service.create_bot_response(response_data)
    return BotResponseResponse.model_validate(response)


@router.get("/chat/{chat_id}/", response_model=MessageListResponse)
async def get_chat_messages(
    chat_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Получить сообщения чата"""
    service = MessageService(db)
    messages = await service.get_chat_messages(chat_id, skip, limit)
    
    # Получаем общее количество сообщений в чате
    total_query = select(func.count(Message.message_id)).where(Message.chat_id == chat_id)
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    return MessageListResponse(
        messages=messages,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/user/{sender_id}/", response_model=MessageListResponse)
async def get_user_messages(
    sender_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Получить сообщения пользователя"""
    service = MessageService(db)
    messages = await service.get_user_messages(sender_id, skip, limit)
    
    # Получаем общее количество сообщений пользователя
    total_query = select(func.count(Message.message_id)).where(
        and_(Message.sender_id == sender_id, Message.sender_type == SenderType.USER)
    )
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    return MessageListResponse(
        messages=messages,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/bot/", response_model=MessageListResponse)
async def get_bot_messages(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Получить сообщения бота"""
    service = MessageService(db)
    messages = await service.get_bot_messages(skip, limit)
    
    # Получаем общее количество сообщений бота
    total_query = select(func.count(Message.message_id)).where(
        Message.sender_type == SenderType.BOT
    )
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    return MessageListResponse(
        messages=messages,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/chat/{chat_id}/stats", response_model=ChatStats)
async def get_chat_stats(
    chat_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить статистику чата"""
    service = MessageService(db)
    stats = await service.get_chat_stats(chat_id)
    return stats


@router.get("/stats/")
async def get_message_stats(
    db: AsyncSession = Depends(get_db)
):
    """Получить общую статистику по сообщениям"""
    service = MessageService(db)
    stats = await service.get_message_stats()
    return stats


@router.get("/search/", response_model=MessageListResponse)
async def search_messages(
    q: str = Query(..., description="Поисковый запрос"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """Поиск сообщений по тексту"""
    service = MessageService(db)
    messages = await service.search_messages(q, skip, limit)
    
    # Получаем общее количество результатов поиска
    total_query = select(func.count(Message.message_id)).where(
        Message.text_content.ilike(f"%{q}%")
    )
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    return MessageListResponse(
        messages=messages,
        total=total,
        page=skip // limit + 1,
        size=limit
    )
