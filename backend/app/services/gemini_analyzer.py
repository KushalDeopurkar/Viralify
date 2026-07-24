import json
import re
from typing import Optional

import google.generativeai as genai

from app.config import settings
from app.models.schemas import NlpFeatures, CvFeatures, VideoFeatures

SYSTEM_INSTRUCTION = """You are Viralify, an expert content virality analyst. You evaluate content using Jonah Berger's STEPPS framework (Social Currency, Triggers, Emotion, Public, Practical Value, Stories) extended with Platform Fit and Hook Quality.

SCORING CALIBRATION:
- 50 = average content (most content lands here)
- 70+ = strong viral potential
- 85+ = exceptional (rare, reserved for truly outstanding content)
- Most content should score between 40-65. Be calibrated and honest.

VERDICTS:
- 85-100: "Will likely go viral"
- 70-84: "Has strong viral potential"
- 55-69: "Good reach potential"
- 40-54: "Average reach"
- 0-39: "Below average reach"

You MUST respond with ONLY valid JSON, no markdown fences, no explanation. Follow the exact schema provided."""

RESPONSE_SCHEMA = """{
  "overall_score": <int 0-100>,
  "verdict": "<string, one of the 5 verdicts above>",
  "dimension_scores": {
    "emotional_impact": {"score": <int 0-100>, "detail": "<one sentence>"},
    "social_currency": {"score": <int 0-100>, "detail": "<one sentence>"},
    "practical_value": {"score": <int 0-100>, "detail": "<one sentence>"},
    "narrative_strength": {"score": <int 0-100>, "detail": "<one sentence>"},
    "trigger_potential": {"score": <int 0-100>, "detail": "<one sentence>"},
    "shareability": {"score": <int 0-100>, "detail": "<one sentence>"},
    "platform_fit": {"score": <int 0-100>, "detail": "<one sentence>"},
    "hook_quality": {"score": <int 0-100>, "detail": "<one sentence>"}
  },
  "emotions_detected": ["<emotion1>", "<emotion2>"],
  "strengths": ["<strength1>", "<strength2>", "<strength3>"],
  "weaknesses": ["<weakness1>", "<weakness2>"],
  "suggestions": [
    {"text": "<actionable suggestion>", "priority": "high|medium|low"},
    {"text": "<actionable suggestion>", "priority": "high|medium|low"},
    {"text": "<actionable suggestion>", "priority": "high|medium|low"}
  ],
  "rewritten_hook": "<improved opening line, or null for images>",
  "thumbnail_suggestions": "<suggestions for visual improvement, or null for text>",
  "best_posting_times": ["<time1>", "<time2>"],
  "recommended_hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "confidence": "high|medium|low"
}"""


def _build_prompt(
    content_type: str,
    platform: str,
    text_content: Optional[str],
    nlp_features: Optional[NlpFeatures],
    cv_features: Optional[CvFeatures],
    video_features: Optional[VideoFeatures],
) -> str:
    parts = [
        f"Analyse this {content_type} content for viral potential on {platform}.",
        f"\nRequired JSON response schema:\n{RESPONSE_SCHEMA}",
    ]

    if content_type == "text" and text_content:
        parts.append(f"\n--- CONTENT ---\n{text_content[:5000]}\n--- END CONTENT ---")

    if nlp_features:
        features_dict = {
            k: v
            for k, v in nlp_features.model_dump().items()
            if v and v != 0 and v != 0.0 and v != [] and v != ""
        }
        parts.append(f"\nPre-computed NLP features:\n{json.dumps(features_dict, indent=2)}")

    if content_type == "image" and cv_features:
        cv_dict = cv_features.model_dump()
        parts.append(f"\nPre-computed visual features:\n{json.dumps(cv_dict, indent=2)}")
        parts.append("\nThe image is attached. Analyse its visual content along with the features above.")

    if content_type == "video" and video_features:
        video_dict = {
            "duration_seconds": video_features.duration_seconds,
            "has_audio": video_features.has_audio,
            "keyframe_count": video_features.keyframe_count,
        }
        parts.append(f"\nVideo metadata:\n{json.dumps(video_dict, indent=2)}")
        if video_features.transcript:
            parts.append(f"\nTranscript:\n{video_features.transcript[:3000]}")
        if video_features.transcript_nlp_features:
            nlp_dict = {
                k: v
                for k, v in video_features.transcript_nlp_features.model_dump().items()
                if v and v != 0 and v != 0.0 and v != [] and v != ""
            }
            parts.append(f"\nTranscript NLP features:\n{json.dumps(nlp_dict, indent=2)}")
        parts.append("\nKeyframes from the video are attached. Analyse the visual content holistically.")

    parts.append(f"\nEvaluate against STEPPS framework for {platform}. Return ONLY valid JSON.")
    return "\n".join(parts)


def _parse_gemini_response(text: str) -> dict:
    """Parse Gemini response, stripping markdown fences if present."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def _call_gemini(
    prompt: str,
    image_bytes: Optional[bytes] = None,
    keyframe_images: Optional[list[bytes]] = None,
) -> dict:
    """Call the Gemini API. Separated for easy mocking in tests."""
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        system_instruction=SYSTEM_INSTRUCTION,
    )

    content_parts = [prompt]

    if image_bytes:
        content_parts.append({"mime_type": "image/jpeg", "data": image_bytes})

    if keyframe_images:
        for i, frame_bytes in enumerate(keyframe_images[:3]):
            content_parts.append({"mime_type": "image/jpeg", "data": frame_bytes})

    response = model.generate_content(content_parts)
    return _parse_gemini_response(response.text)


def analyse_with_gemini(
    content_type: str,
    platform: str,
    text_content: Optional[str],
    image_bytes: Optional[bytes],
    keyframe_images: Optional[list[bytes]],
    nlp_features: Optional[NlpFeatures],
    cv_features: Optional[CvFeatures],
    video_features: Optional[VideoFeatures],
) -> dict:
    """Run Gemini analysis. Returns parsed dict matching AnalyseResponse shape."""
    prompt = _build_prompt(
        content_type, platform, text_content, nlp_features, cv_features, video_features
    )
    return _call_gemini(prompt, image_bytes, keyframe_images)
