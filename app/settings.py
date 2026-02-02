import os
from pathlib import Path
from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Находим местоположение самого файла, затем от него находим .env
dot_env_path = Path(__file__).resolve().parent.parent / ".env"

class Settings(BaseSettings):
    PG_DSN: str
    ES_URL: str
    INDEX_NAME: str
    MAX_RESULTS: int
    model_config = SettingsConfigDict(
        env_file=dot_env_path,
        env_file_encoding="utf-8",
        extra="ignore" # Игнорируем остальные переменные в .env
    )


settings: Settings = Settings()
