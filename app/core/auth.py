"""
Authentication utilities for API
"""
from fastapi import Header, HTTPException
from app.core.config import settings


# TODO: Раскомментировать для продакшена
# async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
#     """
#     Проверка API ключа для n8n запросов.
#     Ожидает заголовок X-API-Key в запросе.
#     """
#     if not settings.N8N_API_KEY:
#         # Если ключ не настроен, пропускаем проверку (для разработки)
#         return
#     
#     if x_api_key != settings.N8N_API_KEY:
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid or missing API key"
#         )
#     
#     return x_api_key

