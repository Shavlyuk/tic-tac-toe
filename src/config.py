from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # База данных
    database_url: str = "sqlite:///./tictactoe.db"

    # Приложение
    app_title: str = "Tic-Tac-Toe API"
    app_version: str = "1.0.0"
    debug: bool = False

    # CORS
    cors_origins: list[str] = ["*"]

    # Логирование
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()