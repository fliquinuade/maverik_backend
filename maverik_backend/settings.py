from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    app_env: str = "prod"

    db_name: str
    db_schema: str
    db_username: str
    db_host: str
    db_port: int = 5432
    db_password: str | None = None

    rag_service_url: str = ""
    frontend_url: str = ""
    portfolio_optimization_url: str = ""

    smtp_api_url: str
    smtp_api_key: str
    mail_sender_name: str
    mail_sender_address: str

    # Clave secreta para tokens PASETO
    secret_key: str = "change_this_in_production"
    
    # Timeout para servicios externos (en segundos)
    external_service_timeout: int = 60


def load_config() -> Settings:
    return Settings()
