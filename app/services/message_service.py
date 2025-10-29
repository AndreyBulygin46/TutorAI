"""
Message service for business logic
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc

from app.models.education import Message, BotResponse, SenderType
from app.schemas.message import (
    MessageCreate, MessageResponse, BotResponseCreate, BotResponseResponse,
    MessageWithResponse, ChatStats
)


class MessageService:
    """Сервис для работы с сообщениями и ответами бота"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_messages(
        self, 
        skip: int = 0, 
        limit: int = 100,
        chat_id: Optional[int] = None,
        sender_type: Optional[SenderType] = None,
        sender_id: Optional[int] = None
    ) -> List[MessageWithResponse]:
        """Получить список сообщений с ответами бота"""
        query = select(Message)
        
        if chat_id is not None:
            query = query.where(Message.chat_id == chat_id)
        
        if sender_type is not None:
            query = query.where(Message.sender_type == sender_type)
        
        if sender_id is not None:
            query = query.where(Message.sender_id == sender_id)
        
        query = query.order_by(desc(Message.created_at)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        # Получаем ответы бота для каждого сообщения
        messages_with_responses = []
        for message in messages:
            bot_responses_query = select(BotResponse).where(
                BotResponse.message_id == message.message_id
            ).order_by(BotResponse.created_at)
            
            bot_responses_result = await self.db.execute(bot_responses_query)
            bot_responses = bot_responses_result.scalars().all()
            
            message_data = MessageWithResponse(
                message_id=message.message_id,
                telegram_message_id=message.telegram_message_id,
                chat_id=message.chat_id,
                sender_type=message.sender_type,
                sender_id=message.sender_id,
                text_content=message.text_content,
                attachment_url=message.attachment_url,
                created_at=message.created_at,
                bot_responses=[
                    BotResponseResponse.model_validate(response) 
                    for response in bot_responses
                ]
            )
            messages_with_responses.append(message_data)
        
        return messages_with_responses
    
    async def get_message_by_id(self, message_id: int) -> Optional[MessageWithResponse]:
        """Получить сообщение по ID с ответами бота"""
        query = select(Message).where(Message.message_id == message_id)
        result = await self.db.execute(query)
        message = result.scalar_one_or_none()
        
        if not message:
            return None
        
        # Получаем ответы бота
        bot_responses_query = select(BotResponse).where(
            BotResponse.message_id == message.message_id
        ).order_by(BotResponse.created_at)
        
        bot_responses_result = await self.db.execute(bot_responses_query)
        bot_responses = bot_responses_result.scalars().all()
        
        return MessageWithResponse(
            message_id=message.message_id,
            telegram_message_id=message.telegram_message_id,
            chat_id=message.chat_id,
            sender_type=message.sender_type,
            sender_id=message.sender_id,
            text_content=message.text_content,
            attachment_url=message.attachment_url,
            created_at=message.created_at,
            bot_responses=[
                BotResponseResponse.model_validate(response) 
                for response in bot_responses
            ]
        )
    
    async def create_message(self, message_data: MessageCreate) -> Message:
        """Создать новое сообщение"""
        message = Message(**message_data.model_dump())
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message
    
    async def create_bot_response(self, response_data: BotResponseCreate) -> BotResponse:
        """Создать ответ бота"""
        response = BotResponse(**response_data.model_dump())
        self.db.add(response)
        await self.db.commit()
        await self.db.refresh(response)
        return response
    
    async def get_chat_messages(
        self, 
        chat_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[MessageWithResponse]:
        """Получить сообщения чата"""
        return await self.get_messages(skip, limit, chat_id=chat_id)
    
    async def get_user_messages(
        self, 
        sender_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[MessageWithResponse]:
        """Получить сообщения пользователя"""
        return await self.get_messages(
            skip, limit, sender_id=sender_id, sender_type=SenderType.USER
        )
    
    async def get_bot_messages(
        self, 
        skip: int = 0,
        limit: int = 100
    ) -> List[MessageWithResponse]:
        """Получить сообщения бота"""
        return await self.get_messages(
            skip, limit, sender_type=SenderType.BOT
        )
    
    async def get_chat_stats(self, chat_id: int) -> ChatStats:
        """Получить статистику чата"""
        # Общее количество сообщений
        total_query = select(func.count(Message.message_id)).where(
            Message.chat_id == chat_id
        )
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0
        
        # Сообщения пользователей
        user_query = select(func.count(Message.message_id)).where(
            and_(Message.chat_id == chat_id, Message.sender_type == SenderType.USER)
        )
        user_result = await self.db.execute(user_query)
        user_messages = user_result.scalar() or 0
        
        # Сообщения бота
        bot_query = select(func.count(Message.message_id)).where(
            and_(Message.chat_id == chat_id, Message.sender_type == SenderType.BOT)
        )
        bot_result = await self.db.execute(bot_query)
        bot_messages = bot_result.scalar() or 0
        
        # Последняя активность
        last_activity_query = select(func.max(Message.created_at)).where(
            Message.chat_id == chat_id
        )
        last_activity_result = await self.db.execute(last_activity_query)
        last_activity = last_activity_result.scalar()
        
        # Количество активных пользователей
        active_users_query = select(func.count(func.distinct(Message.sender_id))).where(
            and_(
                Message.chat_id == chat_id,
                Message.sender_type == SenderType.USER
            )
        )
        active_users_result = await self.db.execute(active_users_query)
        active_users = active_users_result.scalar() or 0
        
        return ChatStats(
            chat_id=chat_id,
            total_messages=total,
            user_messages=user_messages,
            bot_messages=bot_messages,
            last_activity=last_activity,
            active_users=active_users
        )
    
    async def get_message_stats(self) -> Dict[str, Any]:
        """Получить общую статистику по сообщениям"""
        # Общее количество сообщений
        total_query = select(func.count(Message.message_id))
        total_result = await self.db.execute(total_query)
        total = total_result.scalar() or 0
        
        # Сообщения по типам отправителей
        by_sender_query = select(
            Message.sender_type,
            func.count(Message.message_id).label('count')
        ).group_by(Message.sender_type)
        
        by_sender_result = await self.db.execute(by_sender_query)
        by_sender = {row.sender_type: row.count for row in by_sender_result}
        
        # Количество чатов
        chats_query = select(func.count(func.distinct(Message.chat_id)))
        chats_result = await self.db.execute(chats_query)
        chats_count = chats_result.scalar() or 0
        
        # Количество ответов бота
        responses_query = select(func.count(BotResponse.response_id))
        responses_result = await self.db.execute(responses_query)
        responses_count = responses_result.scalar() or 0
        
        return {
            'total_messages': total,
            'by_sender_type': by_sender,
            'total_chats': chats_count,
            'total_responses': responses_count
        }
    
    async def search_messages(
        self, 
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[MessageWithResponse]:
        """Поиск сообщений по тексту"""
        query = select(Message).where(
            Message.text_content.ilike(f"%{search_term}%")
        ).order_by(desc(Message.created_at)).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        messages = result.scalars().all()
        
        # Получаем ответы бота для найденных сообщений
        messages_with_responses = []
        for message in messages:
            bot_responses_query = select(BotResponse).where(
                BotResponse.message_id == message.message_id
            ).order_by(BotResponse.created_at)
            
            bot_responses_result = await self.db.execute(bot_responses_query)
            bot_responses = bot_responses_result.scalars().all()
            
            message_data = MessageWithResponse(
                message_id=message.message_id,
                telegram_message_id=message.telegram_message_id,
                chat_id=message.chat_id,
                sender_type=message.sender_type,
                sender_id=message.sender_id,
                text_content=message.text_content,
                attachment_url=message.attachment_url,
                created_at=message.created_at,
                bot_responses=[
                    BotResponseResponse.model_validate(response) 
                    for response in bot_responses
                ]
            )
            messages_with_responses.append(message_data)
        
        return messages_with_responses
