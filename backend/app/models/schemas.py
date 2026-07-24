from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class Platform(str, Enum):
    twitter = "twitter"
    linkedin = "linkedin"
    instagram = "instagram"
    tiktok = "tiktok"
    reddit = "reddit"
    blog = "blog"
    youtube = "youtube"
    general = "general"


class AnalyseRequest(BaseModel):
    content: str = Field(..., min_length=10, max_length=10000)
    platform: Platform = Platform.general
    author_followers: Optional[int] = None
    author_avg_engagement: Optional[float] = None


class DimensionScore(BaseModel):
    score: int = Field(ge=0, le=100)
    detail: str


class Suggestion(BaseModel):
    priority: str  # high, medium, low
    suggestion: str


class NLPFeatures(BaseModel):
    readability: dict
    sentiment: dict
    structure: dict
    engagement_signals: dict
    platform_fit: dict


class AnalyseResponse(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    verdict: str
    dimension_scores: dict[str, DimensionScore]
    emotions_detected: list[str]
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[Suggestion]
    rewritten_hook: str
    best_posting_times: list[str]
    recommended_hashtags: list[str]
    nlp_features: NLPFeatures
    confidence: str  # "high", "medium", "low"


class FeedbackRequest(BaseModel):
    analysis_id: str
    went_viral: bool
    actual_likes: Optional[int] = None
    actual_shares: Optional[int] = None
    actual_comments: Optional[int] = None
    actual_views: Optional[int] = None
