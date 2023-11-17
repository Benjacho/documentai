from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow')
    assistant_id: str = 'asst_jdXJoDFZs5vnhI4pmgRCie77'
    thread_id: str = 'thread_jwNgbPEYBkAjISHrZdQxpYBR'


settings = Settings()
