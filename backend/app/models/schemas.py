from pydantic import BaseModel, Field
from typing import Optional


class DimensionScore(BaseModel):
    score: int = Field(ge=0, le=100)
    detail: str


class DimensionScores(BaseModel):
    emotional_impact: DimensionScore
    social_currency: DimensionScore
    practical_value: DimensionScore
    narrative_strength: DimensionScore
    trigger_potential: DimensionScore
    shareability: DimensionScore
    platform_fit: DimensionScore
    hook_quality: DimensionScore


class Suggestion(BaseModel):
    text: str
    priority: str = Field(pattern=r"^(high|medium|low)$")


class NlpFeatures(BaseModel):
    # Readability
    flesch_reading_ease: float = 0.0
    flesch_kincaid_grade: float = 0.0
    gunning_fog: float = 0.0
    smog_index: float = 0.0
    reading_time_seconds: float = 0.0
    mass_appeal_score: float = 0.0

    # Sentiment
    vader_compound: float = 0.0
    vader_positive: float = 0.0
    vader_negative: float = 0.0
    vader_neutral: float = 0.0
    arousal_level: str = "low"
    arousal_score: float = 0.0
    dominant_tone: str = "neutral"

    # Structure
    word_count: int = 0
    char_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    avg_sentence_length: float = 0.0
    avg_word_length: float = 0.0
    has_questions: bool = False
    question_count: int = 0
    has_list_format: bool = False
    emoji_count: int = 0
    hashtag_count: int = 0
    hashtags: list[str] = []
    mention_count: int = 0
    url_count: int = 0
    has_caps_emphasis: bool = False
    first_line: str = ""

    # Engagement signals
    power_word_count: int = 0
    power_words_found: list[str] = []
    has_cta: bool = False
    has_numbers: bool = False
    has_controversy: bool = False
    has_personal_story: bool = False
    has_curiosity_gap: bool = False
    has_social_proof: bool = False
    has_urgency: bool = False

    # Platform fit
    length_fit_score: float = 0.0
    hashtag_fit_score: float = 0.0
    platform_fit_score: float = 0.0


class CvFeatures(BaseModel):
    width: int = 0
    height: int = 0
    aspect_ratio: float = 0.0
    brightness_score: float = 0.0
    contrast_score: float = 0.0
    dominant_colors: list[list[int]] = []
    face_count: int = 0
    has_text_overlay: bool = False
    detected_text: str = ""
    composition_score: float = 0.0


class VideoFeatures(BaseModel):
    duration_seconds: float = 0.0
    keyframe_count: int = 0
    transcript: str = ""
    has_audio: bool = False
    keyframe_cv_features: list[CvFeatures] = []
    transcript_nlp_features: Optional[NlpFeatures] = None


class QuickAnalyseRequest(BaseModel):
    content: str = Field(min_length=10)
    platform: str = Field(
        default="general",
        pattern=r"^(twitter|linkedin|instagram|tiktok|reddit|youtube|blog|general)$",
    )


class QuickAnalyseResponse(BaseModel):
    content_type: str = "text"
    quick_score: int
    nlp_features: NlpFeatures


class AnalyseResponse(BaseModel):
    content_type: str
    overall_score: int
    verdict: str
    quick_score: Optional[int] = None
    nlp_features: Optional[NlpFeatures] = None
    cv_features: Optional[CvFeatures] = None
    video_features: Optional[VideoFeatures] = None
    dimension_scores: DimensionScores
    emotions_detected: list[str]
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[Suggestion]
    rewritten_hook: Optional[str] = None
    thumbnail_suggestions: Optional[str] = None
    best_posting_times: list[str]
    recommended_hashtags: list[str]
    confidence: str
    processing_time_ms: int


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
