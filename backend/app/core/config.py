import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Carga el archivo .env ubicado en backend/.env si existe
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


class Settings:
    PROJECT_NAME: str = "TechStore API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    DB_HOST: str = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT: int = int(os.getenv("DB_PORT", "3306"))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_NAME: str = os.getenv("DB_NAME", "techstore_db")
    DATABASE_URL_OVERRIDE: str | None = os.getenv("DATABASE_URL")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "techstore_clave_secreta_segura_sena_2026")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
    REQUIRE_AUTH: bool = os.getenv("REQUIRE_AUTH", "false").strip().lower() in ("1", "true", "yes", "si")

    @property
    def server_url(self) -> str:
        pwd = quote_plus(self.DB_PASSWORD)
        auth = f"{self.DB_USER}:{pwd}" if self.DB_PASSWORD else self.DB_USER
        return f"mysql+pymysql://{auth}@{self.DB_HOST}:{self.DB_PORT}/"

    @property
    def database_url(self) -> str:
        if self.DATABASE_URL_OVERRIDE:
            return self.DATABASE_URL_OVERRIDE
        return f"{self.server_url}{self.DB_NAME}?charset=utf8mb4"


settings = Settings()
