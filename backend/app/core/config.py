'''Loads environment variables safely using Pydantic Settings.'''

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    database_url: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()