"""
Configuration centrale de l'application.
Toutes les valeurs sensibles ou variables viennent du fichier .env
(jamais de clé API en dur dans le code).
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Base de données
    database_url: str = "sqlite:///./car_hunter.db"

    # Sécurité / auth
    secret_key: str = "change-me-in-env"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24

    # Recherche par défaut (peut être surchargé par UserSettings en base)
    default_budget_max: int = 10000
    default_km_max: int = 150000
    default_radius_km: int = 100
    hamburg_lat: float = 53.5511
    hamburg_lon: float = 9.9937

    # Notifications
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Scraping
    scrape_interval_minutes: int = 30
    scrape_user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
