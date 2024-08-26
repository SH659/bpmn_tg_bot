from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DEFAULT_TG_BOT_TOKEN: str
    DEFAULT_BOT: str = 'default'
    DEFAULT_CHAT_MODEL: str = 'llama2'
    CUSTOM_CHAT_MODEL: str = 'custom'
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


settings = Settings()
