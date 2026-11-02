from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """
        Настраиваем параметры подключения к PostgreSQL
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    PG_USER: str = "postgres"
    PG_PASSWORD: str = "postgres"
    PG_HOST: str = "localhost"
    PG_PORT: int = 5432
    PG_DBNAME: str = "codeservice"

    # формируем URL для подключения к БД
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.PG_USER}:{self.PG_PASSWORD}"
            f"@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DBNAME}"
            "?sslmode=require"
        )


class TokenSettings(BaseSettings):
    """
        Настраиваем параметры нашего токена
    """
    token_ttl_seconds: int = 300 # время жизни токена в секундах (сейчас 5 мин)


class CORSSettings(BaseSettings):
    """
        Настраиваем CORS (параметры доступа)
    """
    allow_origins: list[str] = Field(default=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ])


class Settings(BaseSettings):
    """
        Общие настройки приложения
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    db: DatabaseSettings = DatabaseSettings()
    token: TokenSettings = TokenSettings()
    cors: CORSSettings = CORSSettings()


settings = Settings()