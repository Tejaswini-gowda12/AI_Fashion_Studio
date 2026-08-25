import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Sustainable Fabric Analyzer and Fashion Design Assistant"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "sustainable-fashion-secret-jwt-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days

    # Database
    DATABASE_URL: str = "sqlite:///./sustainable_fashion.db"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

    # File Storage
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "uploads")
    MAX_UPLOAD_SIZE_MB: int = 10

    # AI Providers (Fabric Analysis)
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    ROBOFLOW_API_KEY: str = "EGAMsNwFPG7Ik25l9iZU"
    ROBOFLOW_MODEL_ID: str = "fabric-material-detection/1"
    AI_VISION_PROVIDER: str = "roboflow"
    AI_LLM_PROVIDER: str = "mock"
    AI_IMAGE_PROVIDER: str = "mock"

    # Visual Search Providers (Options: mock, google_vision, bing)
    VISUAL_SEARCH_PROVIDER: str = "mock"
    GOOGLE_VISION_API_KEY: str = ""
    BING_VISUAL_SEARCH_API_KEY: str = ""
    VISUAL_SEARCH_RESULT_LIMIT: int = 10
    VISUAL_SEARCH_TIMEOUT_SECONDS: int = 15

    # ── AI Outfit Studio Providers ─────────────────────────────────────────────
    # OUTFIT_LLM_PROVIDER: mock | openai | gemini
    OUTFIT_LLM_PROVIDER: str = "mock"
    # OUTFIT_IMAGE_PROVIDER: mock | dalle | gemini | openai
    OUTFIT_IMAGE_PROVIDER: str = "mock"
    OUTFIT_IMAGE_API_KEY: str = ""
    # SHOPPING_SEARCH_PROVIDER: mock | google_cse | authorized_api | affiliate_feed
    SHOPPING_SEARCH_PROVIDER: str = "mock"
    OUTFIT_SHOPPING_PROVIDER: str = "mock"
    SHOPPING_SEARCH_API_KEY: str = ""
    AFFILIATE_FEED_API_KEY: str = ""
    INDIA_DEFAULT_CURRENCY: str = "INR"
    OUTFIT_VARIATION_COUNT: int = 3
    # Google Custom Search Engine (official API – for shopping product search)
    GOOGLE_CUSTOM_SEARCH_API_KEY: str = ""
    GOOGLE_CUSTOM_SEARCH_CX: str = ""
    # Rate limits
    OUTFIT_SEARCH_RESULT_LIMIT: int = 8
    OUTFIT_REQUEST_TIMEOUT_SECONDS: int = 30
    OUTFIT_RATE_LIMIT_PER_MIN: int = 5
    OUTFIT_IMAGE_QUOTA_PER_USER_PER_DAY: int = 10

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
