from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    """
        Схема запроса на авторизацию / аутентификацию пользователя
    """
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)
    
    # удаляем пробелы в начале и конце строк
    model_config = ConfigDict(str_strip_whitespace=True)