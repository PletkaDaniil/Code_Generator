import asyncio
import secrets
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# хеш-пустышка для проверки пароля, если пользователь не найден
# помогает не раскрывать существование аккаунта по времени ответа
DUMMY_HASH = pwd_context.hash("dummy-password")


async def hash_password(password: str) -> str:
    """
        Хешируем пароль
    """
    return await asyncio.to_thread(pwd_context.hash, password)


async def verify_password(
    password: str, hashed: str
) -> bool:
    """
        Проверяем пароль по сохраненному хешу
    """
    return await asyncio.to_thread(pwd_context.verify, password, hashed)


def generate_token() -> str:
    """
        Генерируем случайный токен доступа
    """
    return secrets.token_urlsafe(32)
