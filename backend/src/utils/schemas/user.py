from pydantic import BaseModel


class UserResponse(BaseModel):
    """
        Схема ответа с данными пользователя
    """
    id: int
    username: str