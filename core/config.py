from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    database_url: str
    host: str = "0.0.0.0"
    port: int = 8000


settings = Settings()