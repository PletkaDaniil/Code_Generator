from pydantic import BaseModel


class CodeResponse(BaseModel):
    """
        Схема ответа с одноразовым кодом доступа
    """
    code: str