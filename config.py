from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BOT_TOKEN: str
    WEBAPP_URL: str
    WEBHOOK_SECRET: str = "secret"
    DATABASE_URL: str = "sqlite+aiosqlite:///./chat.db"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
