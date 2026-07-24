import logging

from app.config import settings

logger = logging.getLogger(__name__)


def _get_client():
    """Lazy-init Supabase client."""
    if not settings.supabase_url or not settings.supabase_service_key:
        return None
    try:
        from supabase import create_client
        return create_client(settings.supabase_url, settings.supabase_service_key)
    except Exception as e:
        logger.warning(f"Supabase client init failed: {e}")
        return None


def save_analysis(data: dict) -> None:
    """Fire-and-forget save to Supabase. Never raises."""
    try:
        client = _get_client()
        if not client:
            return
        client.table("analyses").insert(data).execute()
    except Exception as e:
        logger.warning(f"Failed to save analysis: {e}")
