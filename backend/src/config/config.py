from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


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
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.PG_USER,
            password=self.PG_PASSWORD,
            host=self.PG_HOST,
            port=self.PG_PORT,
            database=self.PG_DBNAME,
            query={"sslmode": "require"}
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
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

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