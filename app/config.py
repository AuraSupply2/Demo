from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    app_name: str = "Negocio Demo"
    debug: bool = False
    secret_key: str = "cambia-esto"

    class Config:
        env_file = ".env"


settings = Settings()