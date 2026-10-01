from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Local Data Assistant"
    app_version: str = "0.0.1"

    api_host: str = "0.0.0.0"
    api_port: int = 8000

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_database: str = "data_assistant"
    postgres_user: str = "data_assistant"
    postgres_password: str = "change_me"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen3:8b"

    debug: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()