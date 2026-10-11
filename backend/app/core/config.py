import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Community Event Management and Participation System (CEMPS)")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api")
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY", "cemps_super_secret_jwt_key_college_project_2026_engagement_platform"
    )
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cemps.db")

    @property
    def cors_origins(self) -> List[str]:
        raw = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5500,http://localhost:8000,http://127.0.0.1:5500,http://127.0.0.1:8000,http://127.0.0.1:3000,null",
        )
        return [origin.strip() for origin in raw.split(",") if origin.strip()]


settings = Settings()
