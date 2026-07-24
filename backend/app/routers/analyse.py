import asyncio
import time
import threading
from typing import Optional

from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from app.config import settings
from app.models.schemas import (
    AnalyseResponse,
    QuickAnalyseRequest,
    QuickAnalyseResponse,
    HealthResponse,
    DimensionScores,
    DimensionScore,
    Suggestion,
)
from app.services.nlp_analyzer import analyse_text, compute_quick_score
from app.services.image_analyzer import analyse_image
from app.services.video_analyzer import analyse_video
from app.services.gemini_analyzer import analyse_with_gemini
from app.services.database import save_analysis

router = APIRouter()

VALID_PLATFORMS = {"twitter", "linkedin", "instagram", "tiktok", "reddit", "youtube", "blog", "general"}
VALID_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
VALID_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm"}


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse()


@router.post("/analyse/quick", response_model=QuickAnalyseResponse)
async def quick_analyse(request: QuickAnalyseRequest):
    if len(request.content) < 10:
        raise HTTPException(status_code=422, detail="Content must be at least 10 characters")

    nlp_features = analyse_text(request.content, request.platform)
    quick_score = compute_quick_score(nlp_features)

    return QuickAnalyseResponse(
        content_type="text",
        quick_score=quick_score,
        nlp_features=nlp_features,
    )


@router.post("/analyse", response_model=AnalyseResponse)
async def full_analyse(
    content_type: str = Form(default="text"),
    content: Optional[str] = Form(default=None),
    platform: str = Form(default="general"),
    file: Optional[UploadFile] = File(default=None),
    author_followers: Optional[int] = Form(default=None),
    author_avg_engagement: Optional[float] = Form(default=None),
):
    start_time = time.time()

    if platform not in VALID_PLATFORMS:
        raise HTTPException(status_code=422, detail=f"Invalid platform. Must be one of: {', '.join(VALID_PLATFORMS)}")

    if content_type not in {"text", "image", "video"}:
        raise HTTPException(status_code=422, detail="content_type must be text, image, or video")

    nlp_features = None
    cv_features = None
    video_features = None
    image_bytes = None
    keyframe_images = None
    quick_score = None
    text_content = content

    # Phase 1: Local feature extraction
    if content_type == "text":
        if not content or len(content.strip()) < 10:
            raise HTTPException(status_code=422, detail="Text content must be at least 10 characters")
        if len(content) > 10000:
            text_content = content[:5000]
        nlp_features = analyse_text(content, platform)
        quick_score = compute_quick_score(nlp_features)

    elif content_type == "image":
        if not file:
            raise HTTPException(status_code=422, detail="Image file is required")
        if file.content_type not in VALID_IMAGE_TYPES:
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported image format. Supported: {', '.join(VALID_IMAGE_TYPES)}",
            )
        image_bytes = await file.read()
        if len(image_bytes) > settings.max_image_size_mb * 1024 * 1024:
            raise HTTPException(status_code=422, detail=f"Image exceeds {settings.max_image_size_mb}MB limit")
        cv_features = analyse_image(image_bytes)
        # If image has text overlay, run NLP on it
        if cv_features.detected_text:
            nlp_features = analyse_text(cv_features.detected_text, platform)

    elif content_type == "video":
        if not file:
            raise HTTPException(status_code=422, detail="Video file is required")
        if file.content_type not in VALID_VIDEO_TYPES:
            raise HTTPException(
                status_code=422,
                detail=f"Unsupported video format. Supported: {', '.join(VALID_VIDEO_TYPES)}",
            )
        video_bytes = await file.read()
        if len(video_bytes) > settings.max_video_size_mb * 1024 * 1024:
            raise HTTPException(status_code=422, detail=f"Video exceeds {settings.max_video_size_mb}MB limit")
        video_features, keyframe_images = analyse_video(video_bytes, platform)
        if video_features.duration_seconds > settings.max_video_duration_seconds:
            raise HTTPException(
                status_code=422,
                detail=f"Video exceeds {settings.max_video_duration_seconds}s limit",
            )
        nlp_features = video_features.transcript_nlp_features
        text_content = video_features.transcript or None

    # Phase 2: Gemini analysis (synchronous SDK call — run off the event loop)
    try:
        gemini_result = await asyncio.to_thread(
            analyse_with_gemini,
            content_type=content_type,
            platform=platform,
            text_content=text_content,
            image_bytes=image_bytes,
            keyframe_images=keyframe_images,
            nlp_features=nlp_features,
            cv_features=cv_features,
            video_features=video_features,
        )
    except Exception:
        # Retry once
        try:
            gemini_result = await asyncio.to_thread(
                analyse_with_gemini,
                content_type=content_type,
                platform=platform,
                text_content=text_content,
                image_bytes=image_bytes,
                keyframe_images=keyframe_images,
                nlp_features=nlp_features,
                cv_features=cv_features,
                video_features=video_features,
            )
        except Exception as e:
            # Fall back to quick score for text
            if content_type == "text" and quick_score is not None:
                raise HTTPException(
                    status_code=502,
                    detail=f"AI analysis failed. Quick score: {quick_score}/100. Error: {str(e)[:200]}",
                )
            raise HTTPException(status_code=502, detail=f"AI analysis unavailable: {str(e)[:200]}")

    processing_time = int((time.time() - start_time) * 1000)

    response = AnalyseResponse(
        content_type=content_type,
        overall_score=gemini_result["overall_score"],
        verdict=gemini_result["verdict"],
        quick_score=quick_score,
        nlp_features=nlp_features,
        cv_features=cv_features,
        video_features=video_features,
        dimension_scores=DimensionScores(**{
            k: DimensionScore(**v)
            for k, v in gemini_result["dimension_scores"].items()
        }),
        emotions_detected=gemini_result["emotions_detected"],
        strengths=gemini_result["strengths"],
        weaknesses=gemini_result["weaknesses"],
        suggestions=[Suggestion(**s) for s in gemini_result["suggestions"]],
        rewritten_hook=gemini_result.get("rewritten_hook"),
        thumbnail_suggestions=gemini_result.get("thumbnail_suggestions"),
        best_posting_times=gemini_result["best_posting_times"],
        recommended_hashtags=gemini_result["recommended_hashtags"],
        confidence=gemini_result["confidence"],
        processing_time_ms=processing_time,
    )

    # Fire-and-forget DB save
    db_data = {
        "content_type": content_type,
        "content_text": (content or "")[:5000] if content_type == "text" else None,
        "platform": platform,
        "overall_score": response.overall_score,
        "quick_score": quick_score,
        "dimension_scores": gemini_result["dimension_scores"],
        "nlp_features": nlp_features.model_dump() if nlp_features else {},
        "cv_features": cv_features.model_dump() if cv_features else {},
        "video_features": {"duration": video_features.duration_seconds, "has_audio": video_features.has_audio} if video_features else {},
        "suggestions": [s.model_dump() for s in response.suggestions],
        "gemini_response": gemini_result,
        "processing_time_ms": processing_time,
    }
    threading.Thread(target=save_analysis, args=(db_data,), daemon=True).start()

    return response
