import os.path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PORT: int
    DIAGRAM_SERVICE_API_URL: str
    DEFAULT_TG_BOT_TOKEN: str
    DEFAULT_BOT: str = 'default'
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), '.env'),
        env_file_encoding='utf-8'
    )


settings = Settings()
