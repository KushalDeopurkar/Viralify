import pytest


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"


import io
from unittest.mock import patch, MagicMock

from PIL import Image


MOCK_GEMINI = {
    "overall_score": 65,
    "verdict": "Good reach potential",
    "dimension_scores": {
        "emotional_impact": {"score": 60, "detail": "Moderate emotion."},
        "social_currency": {"score": 65, "detail": "Informative."},
        "practical_value": {"score": 70, "detail": "Useful tips."},
        "narrative_strength": {"score": 55, "detail": "Light narrative."},
        "trigger_potential": {"score": 60, "detail": "Some triggers."},
        "shareability": {"score": 68, "detail": "Tag-worthy."},
        "platform_fit": {"score": 72, "detail": "Good fit."},
        "hook_quality": {"score": 62, "detail": "Decent hook."},
    },
    "emotions_detected": ["interest", "curiosity"],
    "strengths": ["Clear message", "Good length", "Has CTA"],
    "weaknesses": ["Weak hook", "No story"],
    "suggestions": [
        {"text": "Improve the hook.", "priority": "high"},
        {"text": "Add a story.", "priority": "medium"},
        {"text": "Use trending hashtags.", "priority": "low"},
    ],
    "rewritten_hook": "Stop scrolling — this changes everything.",
    "thumbnail_suggestions": None,
    "best_posting_times": ["Monday 8am", "Wednesday 12pm"],
    "recommended_hashtags": ["#tips", "#growth", "#viral", "#content", "#marketing"],
    "confidence": "medium",
}


@pytest.mark.asyncio
async def test_quick_analyse(client):
    resp = await client.post(
        "/api/analyse/quick",
        json={"content": "This is a great post about marketing tips!", "platform": "twitter"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "quick_score" in data
    assert 0 <= data["quick_score"] <= 100
    assert data["content_type"] == "text"


@pytest.mark.asyncio
async def test_quick_analyse_too_short(client):
    resp = await client.post(
        "/api/analyse/quick",
        json={"content": "Hi", "platform": "twitter"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
@patch("app.routers.analyse.analyse_with_gemini")
@patch("app.routers.analyse.save_analysis")
async def test_full_analyse_text(mock_save, mock_gemini, client):
    mock_gemini.return_value = MOCK_GEMINI
    resp = await client.post(
        "/api/analyse",
        data={"content_type": "text", "content": "Amazing marketing hack that will blow your mind!", "platform": "twitter"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["overall_score"] == 65
    assert data["content_type"] == "text"
    assert len(data["suggestions"]) == 3


@pytest.mark.asyncio
@patch("app.routers.analyse.analyse_with_gemini")
@patch("app.routers.analyse.save_analysis")
async def test_full_analyse_image(mock_save, mock_gemini, client):
    mock_gemini.return_value = MOCK_GEMINI
    img = Image.new("RGB", (200, 200), (255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    resp = await client.post(
        "/api/analyse",
        data={"content_type": "image", "platform": "instagram"},
        files={"file": ("test.jpg", buf, "image/jpeg")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["content_type"] == "image"
    assert data["cv_features"]["width"] == 200


@pytest.mark.asyncio
async def test_invalid_platform(client):
    resp = await client.post(
        "/api/analyse",
        data={"content_type": "text", "content": "Test content here", "platform": "fakebook"},
    )
    assert resp.status_code == 422
