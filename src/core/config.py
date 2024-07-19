import os
from logging import config as logging_config

from core.logger import LOGGING
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
from pathlib import Path

logging_config.dictConfig(LOGGING)


BASE_DIR = PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class RedisSettings(BaseModel):
    """Настройки подключения к redis"""

    host: str = "127.0.0.1"
    port: int = 6379


class ElasticSettings(BaseModel):
    """Настрокий подключения к elasctisearch"""

    host: str = "127.0.0.1"
    port: int = 9200
    scheme: str = "http"


class Settings(BaseSettings):
    """Главный класс настроек всего приложения"""

    project_name: str = "movies"
    app_port: int = 8000
    redis: RedisSettings = RedisSettings()
    es: ElasticSettings = ElasticSettings()

    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )


settings = Settings()
