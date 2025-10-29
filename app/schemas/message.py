"""
Pydantic schemas for Message and Bot Response API
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.education import SenderType


class MessageBase(BaseModel):
    """Базовая схема сообщения"""
    chat_id: int = Field(..., description="ID чата")
    sender_type: SenderType = Field(..., description="Тип отправителя")
    sender_id: Optional[int] = Field(None, description="ID отправителя")
    text_content: Optional[str] = Field(None, description="Текст сообщения")
    attachment_url: Optional[str] = Field(None, description="URL вложения")


class MessageCreate(MessageBase):
    """Схема для создания сообщения"""
    telegram_message_id: Optional[int] = Field(None, description="Telegram Message ID")


class MessageResponse(MessageBase):
    """Схема ответа для сообщения"""
    model_config = ConfigDict(from_attributes=True)
    
    message_id: int = Field(..., description="ID сообщения")
    telegram_message_id: Optional[int] = Field(None, description="Telegram Message ID")
    created_at: datetime = Field(..., description="Дата создания")


class BotResponseBase(BaseModel):
    """Базовая схема ответа бота"""
    text_content: Optional[str] = Field(None, description="Текст ответа")
    attachment_url: Optional[str] = Field(None, description="URL вложения")


class BotResponseCreate(BotResponseBase):
    """Схема для создания ответа бота"""
    message_id: int = Field(..., description="ID сообщения")


class BotResponseResponse(BotResponseBase):
    """Схема ответа для ответа бота"""
    model_config = ConfigDict(from_attributes=True)
    
    response_id: int = Field(..., description="ID ответа")
    message_id: int = Field(..., description="ID сообщения")
    created_at: datetime = Field(..., description="Дата создания")


class MessageWithResponse(MessageResponse):
    """Сообщение с ответом бота"""
    bot_responses: List[BotResponseResponse] = Field(default_factory=list)


class MessageListResponse(BaseModel):
    """Схема для списка сообщений"""
    messages: List[MessageWithResponse]
    total: int = Field(..., description="Общее количество сообщений")
    page: int = Field(..., description="Текущая страница")
    size: int = Field(..., description="Размер страницы")


class ChatStats(BaseModel):
    """Статистика чата"""
    chat_id: int
    total_messages: int
    user_messages: int
    bot_messages: int
    last_activity: Optional[datetime]
    active_users: int
