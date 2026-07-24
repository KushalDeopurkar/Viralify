from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    gemini_api_key: str = ""
    groq_api_key: str = ""
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_key: str = ""
    cors_origins: str = "http://localhost:3000"
    max_video_duration_seconds: int = 60
    max_image_size_mb: int = 10
    max_video_size_mb: int = 50

    class Config:
        env_file = ".env"


settings = Settings()
