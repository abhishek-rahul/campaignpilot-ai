from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "CampaignPilot AI"
    app_env: str = "local"
    app_debug: bool = True
    api_v1_prefix: str = "/api/v1"

    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    database_url: str = "postgresql+psycopg://campaignpilot:campaignpilot@localhost:5432/campaignpilot"
    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_document_index: str = "campaignpilot_document_chunks"
    upload_dir: str = "../uploads/documents"

    openai_api_key: str = "replace_me"
    openai_chat_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    telegram_bot_token: str = "replace_me"
    telegram_default_chat_id: str = "replace_me"
    telegram_chat_id: str = "replace_me"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
