from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

    database_url: str
    source_database_url: str | None = None
    database_echo: bool = False
    database_pool_size: int = 5
    database_max_overflow: int = 10

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    encryption_key: str

    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str | None = None
    smtp_password: str | None = None
    email_from: str = "noreply@minigovern.local"

    country_api: str = "https://restcountries.com/v3.1/name"


settings = Settings()