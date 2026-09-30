from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PROJECT_NAME: str = "AI News Research & Content Generator"
    DATABASE_URL: str = "sqlite:///./news_scraper.db"
    SECRET_KEY: str = "supersecretkey"
    GOOGLE_API_KEY: str = ""
    GOOGLE_CSE_ID: str = ""
    GEMINI_API_KEY: str = ""

settings = Settings()

# Centralized Content Type Configuration
SHORT_FORM_CONFIG = {
    "max_sources": 8,
    "research_depth": "light",
    "context_depth": "minimal",
    "fact_depth": "essential",
    "script_depth": "short",
    "credits": 10
}

LONG_FORM_CONFIG = {
    "max_sources": 20,
    "research_depth": "deep",
    "context_depth": "detailed",
    "fact_depth": "comprehensive",
    "script_depth": "long",
    "credits": 25
}

def get_content_config(content_type: str) -> dict:
    normalized = content_type.lower().replace("_", " ")
    if normalized == "short form":
        return SHORT_FORM_CONFIG
    elif normalized == "long form":
        return LONG_FORM_CONFIG
    return SHORT_FORM_CONFIG  # Default
