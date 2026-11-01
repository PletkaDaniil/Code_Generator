from pydantic import BaseModel


class TokenResponse(BaseModel):
    """
        Схема ответа с токеном и временем его действия
    """
    token: str
    expires_in: int