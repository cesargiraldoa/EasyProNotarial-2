from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"
DEFAULT_DATABASE_PATH = BASE_DIR / "easypro2.db"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}"

# Load backend/.env early so imports that call get_settings() at module scope
# see the same values even before app.main runs.
load_dotenv(ENV_FILE, override=False)


class Settings(BaseSettings):
    app_name: str = "EasyPro 2 API"
    environment: str = "development"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    frontend_url: str = "http://localhost:5179"
    api_public_url: str = ""
    onlyoffice_documentserver_url: str = "http://localhost:8082"
    onlyoffice_jwt_secret: str = ""
    database_url: str = DEFAULT_DATABASE_URL
    secret_key: str = "change-this-in-production"
    access_token_expire_minutes: int = 480
    openai_api_key: str = ""
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = ""
    celery_result_backend: str = ""
    notarial_intelligence_storage_bucket: str = "documentos"
    notarial_intelligence_storage_prefix: str = "notarial-intelligence"
    notarial_intelligence_local_storage_dir: str = str(BASE_DIR / "storage" / "notarial-intelligence")
    gari_billing_base_url: str = ""
    gari_billing_internal_key: str = ""
    gari_billing_timeout_seconds: int = 30

    model_config = SettingsConfigDict(env_file=str(ENV_FILE), env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
