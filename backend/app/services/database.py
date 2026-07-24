"""
Supabase integration for persisting analyses and user data.
"""

import json
from supabase import create_client, Client
from app.config import get_settings


_client: Client | None = None


def get_db() -> Client:
    global _client
    if _client is None:
        settings = get_settings()
        _client = create_client(settings.supabase_url, settings.supabase_service_key)
    return _client


async def save_analysis(user_id: str | None, analysis_data: dict) -> dict:
    db = get_db()
    row = {
        "content_text": analysis_data.get("content", "")[:5000],
        "platform": analysis_data.get("platform", "general"),
        "overall_score": analysis_data.get("overall_score", 0),
        "dimension_scores": json.dumps(analysis_data.get("dimension_scores", {})),
        "nlp_features": json.dumps(analysis_data.get("nlp_features", {})),
        "suggestions": json.dumps(analysis_data.get("suggestions", [])),
        "claude_response": json.dumps(analysis_data.get("claude_response", {})),
    }
    if user_id:
        row["user_id"] = user_id

    result = db.table("analyses").insert(row).execute()
    return result.data[0] if result.data else {}


async def get_user_analyses(user_id: str, limit: int = 20) -> list:
    db = get_db()
    result = (
        db.table("analyses")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data or []


async def save_feedback(analysis_id: str, feedback_data: dict) -> dict:
    db = get_db()
    row = {
        "analysis_id": analysis_id,
        "actually_went_viral": feedback_data.get("went_viral", False),
        "actual_engagement": json.dumps({
            "likes": feedback_data.get("actual_likes"),
            "shares": feedback_data.get("actual_shares"),
            "comments": feedback_data.get("actual_comments"),
            "views": feedback_data.get("actual_views"),
        }),
    }
    result = db.table("feedback").insert(row).execute()
    return result.data[0] if result.data else {}
