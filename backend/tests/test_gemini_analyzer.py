import json
import pytest
from unittest.mock import patch, MagicMock

from app.services.gemini_analyzer import analyse_with_gemini, _build_prompt
from app.models.schemas import NlpFeatures, CvFeatures, VideoFeatures


MOCK_GEMINI_RESPONSE = {
    "overall_score": 72,
    "verdict": "Has strong viral potential",
    "dimension_scores": {
        "emotional_impact": {"score": 75, "detail": "Strong emotional resonance."},
        "social_currency": {"score": 70, "detail": "Makes sharer look informed."},
        "practical_value": {"score": 65, "detail": "Actionable tips present."},
        "narrative_strength": {"score": 68, "detail": "Decent story arc."},
        "trigger_potential": {"score": 72, "detail": "Connected to daily routine."},
        "shareability": {"score": 78, "detail": "Highly tag-worthy."},
        "platform_fit": {"score": 80, "detail": "Good format for platform."},
        "hook_quality": {"score": 70, "detail": "Opening grabs attention."},
    },
    "emotions_detected": ["awe", "curiosity"],
    "strengths": ["Strong hook", "Good emotional tone", "Platform-appropriate length"],
    "weaknesses": ["Could use more data points", "Missing call-to-action"],
    "suggestions": [
        {"text": "Add a specific statistic to boost credibility.", "priority": "high"},
        {"text": "End with a clear call-to-action.", "priority": "medium"},
        {"text": "Consider adding relevant hashtags.", "priority": "low"},
    ],
    "rewritten_hook": "Here's what nobody tells you about content that goes viral:",
    "thumbnail_suggestions": None,
    "best_posting_times": ["Tuesday 9am EST", "Thursday 6pm EST"],
    "recommended_hashtags": ["#contentcreation", "#viral", "#growthhacks", "#marketing", "#socialmedia"],
    "confidence": "medium",
}


class TestBuildPrompt:
    def test_text_prompt_includes_content(self):
        features = NlpFeatures(word_count=50, vader_compound=0.5)
        prompt = _build_prompt("text", "twitter", "Hello world", features, None, None)
        assert "Hello world" in prompt
        assert "twitter" in prompt
        assert "STEPPS" in prompt

    def test_image_prompt_includes_cv_features(self):
        cv = CvFeatures(width=1080, height=1080, face_count=2, brightness_score=72.0)
        prompt = _build_prompt("image", "instagram", None, None, cv, None)
        assert "instagram" in prompt
        assert "1080" in prompt

    def test_video_prompt_includes_transcript(self):
        video = VideoFeatures(
            duration_seconds=30.0,
            transcript="Hello everyone welcome to my channel",
            has_audio=True,
        )
        prompt = _build_prompt("video", "tiktok", None, None, None, video)
        assert "Hello everyone" in prompt
        assert "tiktok" in prompt


class TestAnalyseWithGemini:
    @patch("app.services.gemini_analyzer._call_gemini")
    def test_text_analysis_returns_valid_response(self, mock_call):
        mock_call.return_value = MOCK_GEMINI_RESPONSE
        features = NlpFeatures(word_count=50, vader_compound=0.5)
        result = analyse_with_gemini(
            content_type="text",
            platform="twitter",
            text_content="Test content here",
            image_bytes=None,
            keyframe_images=None,
            nlp_features=features,
            cv_features=None,
            video_features=None,
        )
        assert result["overall_score"] == 72
        assert result["verdict"] == "Has strong viral potential"
        assert len(result["suggestions"]) == 3
        assert result["dimension_scores"]["emotional_impact"]["score"] == 75

    @patch("app.services.gemini_analyzer._call_gemini")
    def test_image_analysis(self, mock_call):
        mock_call.return_value = MOCK_GEMINI_RESPONSE
        cv = CvFeatures(width=1080, height=1080)
        result = analyse_with_gemini(
            content_type="image",
            platform="instagram",
            text_content=None,
            image_bytes=b"fake_image_bytes",
            keyframe_images=None,
            nlp_features=None,
            cv_features=cv,
            video_features=None,
        )
        assert result["overall_score"] == 72

    @patch("app.services.gemini_analyzer._call_gemini")
    def test_gemini_failure_raises(self, mock_call):
        mock_call.side_effect = Exception("API Error")
        features = NlpFeatures(word_count=50)
        with pytest.raises(Exception, match="API Error"):
            analyse_with_gemini(
                content_type="text",
                platform="twitter",
                text_content="Test",
                image_bytes=None,
                keyframe_images=None,
                nlp_features=features,
                cv_features=None,
                video_features=None,
            )
