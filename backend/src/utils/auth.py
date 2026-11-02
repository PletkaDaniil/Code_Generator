from typing import Annotated
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.database.crud import get_user_id_by_token
from src.database.database import DbSession
from src.utils.exceptions import AppError

bearer_scheme = HTTPBearer(auto_error=False)
BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None, 
    Depends(bearer_scheme)
]


async def get_current_user_id(
    db: DbSession, credentials: BearerCredentials
) -> int:
    """
        Получаем user_id владельца токена
    """
    user_id = None
    if credentials is not None:
        user_id = await get_user_id_by_token(db, credentials.credentials)

    if user_id is None:
        raise AppError(401, "Требуется вход: токен отсутствует или истёк")
    return user_id
