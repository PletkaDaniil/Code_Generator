from pydantic import BaseModel, ConfigDict, Field


class RegisterRequest(BaseModel):
    """
        Схема запроса на регистрацию пользователя
    """
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=6, max_length=128)
    
    # удаляем пробелы в начале и конце строк
    model_config = ConfigDict(str_strip_whitespace=True)