from fastapi import APIRouter, HTTPException
from app.models.schemas import AnalyseRequest, AnalyseResponse
from app.services.nlp_analyzer import NLPAnalyzer
from app.services.claude_analyzer import ClaudeAnalyzer
from app.services.database import save_analysis

router = APIRouter(prefix="/api", tags=["analysis"])

nlp = NLPAnalyzer()
claude = ClaudeAnalyzer()


@router.post("/analyse", response_model=None)
async def analyse_content(request: AnalyseRequest):
    """
    Main analysis endpoint.
    1. Run local NLP pipeline (~50ms)
    2. Send to Claude for deep STEPPS analysis (~2-4s)
    3. Merge results and return
    """

    # Step 1: Local NLP features
    nlp_features = nlp.analyse(request.content, request.platform.value)

    # Step 2: Claude deep analysis
    claude_result = await claude.analyse(
        content=request.content,
        platform=request.platform.value,
        nlp_features=nlp_features,
        author_followers=request.author_followers,
        author_avg_engagement=request.author_avg_engagement,
    )

    if "error" in claude_result:
        raise HTTPException(status_code=502, detail=claude_result["error"])

    # Step 3: Merge and return
    response = {
        **claude_result,
        "nlp_features": nlp_features,
    }

    # Step 4: Save to DB (fire and forget — don't block response)
    try:
        await save_analysis(
            user_id=None,  # TODO: extract from auth header
            analysis_data={
                "content": request.content,
                "platform": request.platform.value,
                "overall_score": claude_result.get("overall_score", 0),
                "dimension_scores": claude_result.get("dimension_scores", {}),
                "nlp_features": nlp_features,
                "suggestions": claude_result.get("suggestions", []),
                "claude_response": claude_result,
            },
        )
    except Exception:
        pass  # DB save failure shouldn't break the response

    return response


@router.post("/analyse/quick")
async def quick_analyse(request: AnalyseRequest):
    """
    NLP-only analysis. No Claude API call. Instant results.
    Good for real-time typing feedback.
    """
    features = nlp.analyse(request.content, request.platform.value)

    # Compute a quick score from NLP features
    scores = {
        "readability": features["readability"]["mass_appeal_score"],
        "sentiment_arousal": features["sentiment"]["arousal_score"],
        "platform_fit": features["platform_fit"]["overall_platform_score"],
        "engagement_signals": min(100, features["engagement_signals"]["power_word_count"] * 15 + 30),
    }
    quick_score = round(sum(scores.values()) / len(scores))

    return {
        "quick_score": quick_score,
        "component_scores": scores,
        "nlp_features": features,
    }
