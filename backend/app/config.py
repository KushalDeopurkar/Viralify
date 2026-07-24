from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    anthropic_api_key: str = ""
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""
    cors_origins: str = "http://localhost:3000"

    # Rate limits
    free_tier_daily_limit: int = 5
    pro_tier_daily_limit: int = 100

    # Claude config
    claude_model: str = "claude-sonnet-4-6"
    claude_max_tokens: int = 2000

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
