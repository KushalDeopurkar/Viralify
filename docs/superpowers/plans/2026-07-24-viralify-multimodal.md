# Viralify multimodal implementation plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a full-stack web app that predicts content virality across text, images, and video using local feature extraction + Google Gemini API for STEPPS framework scoring.

**Architecture:** Two-phase pipeline. Phase 1 extracts features locally per content type (NLP for text, OpenCV/Pillow for images, FFmpeg+Whisper for video). Phase 2 sends content + features to Gemini for STEPPS evaluation returning structured JSON scores. Frontend is a single-page Next.js app with animated results visualization.

**Tech Stack:** FastAPI (Python 3.12+), Next.js 14+ (TypeScript), Tailwind CSS, Recharts, Framer Motion, Google Gemini API, Groq Whisper API, Supabase (PostgreSQL), textstat, vaderSentiment, NLTK, OpenCV, Pillow, FFmpeg.

## Global constraints

- Zero budget. All services must use free tiers only.
- Gemini free tier: 1,500 req/day, 10 RPM. Groq Whisper: 2,000 req/day.
- Render free tier: 512MB RAM, cold starts after inactivity.
- All scores are integers 0-100. Calibration: 50 = average, 70+ = strong, 85+ = exceptional.
- Backend: snake_case, Pydantic models for all I/O, async endpoints.
- Frontend: TypeScript strict, no `any` types.
- DB writes are fire-and-forget. Never block the response on a save failure.
- No auth for MVP. Anonymous analyses only.

---

## File map

### Backend (create all)

| File | Responsibility |
|---|---|
| `backend/app/__init__.py` | Package init |
| `backend/app/main.py` | FastAPI app, CORS, lifespan, mount routers |
| `backend/app/config.py` | Pydantic Settings from env vars |
| `backend/app/models/__init__.py` | Package init |
| `backend/app/models/schemas.py` | All request/response Pydantic models |
| `backend/app/routers/__init__.py` | Package init |
| `backend/app/routers/analyse.py` | POST /api/analyse, POST /api/analyse/quick, GET /api/health |
| `backend/app/services/__init__.py` | Package init |
| `backend/app/services/nlp_analyzer.py` | Text feature extraction (textstat, VADER, NLTK) |
| `backend/app/services/image_analyzer.py` | Image feature extraction (Pillow, OpenCV, pytesseract, sklearn) |
| `backend/app/services/video_analyzer.py` | FFmpeg keyframe extraction + pipeline orchestration |
| `backend/app/services/whisper_client.py` | Groq Whisper transcription |
| `backend/app/services/gemini_analyzer.py` | Gemini API for STEPPS scoring (text + vision) |
| `backend/app/services/database.py` | Supabase persistence (fire-and-forget) |
| `backend/requirements.txt` | Python dependencies |
| `backend/.env.example` | Environment variable template |
| `backend/Dockerfile` | Container with FFmpeg + Tesseract |
| `backend/supabase_migration.sql` | Database schema |
| `tests/test_nlp_analyzer.py` | NLP unit tests |
| `tests/test_image_analyzer.py` | Image analyzer unit tests |
| `tests/test_video_analyzer.py` | Video analyzer unit tests |
| `tests/test_gemini_analyzer.py` | Gemini integration tests (mocked) |
| `tests/test_api.py` | API endpoint integration tests |
| `tests/conftest.py` | Shared fixtures |

### Frontend (create all)

| File | Responsibility |
|---|---|
| `frontend/package.json` | Dependencies and scripts |
| `frontend/next.config.js` | Next.js config |
| `frontend/tailwind.config.ts` | Tailwind with custom palette |
| `frontend/tsconfig.json` | TypeScript strict config |
| `frontend/.env.local.example` | Env template |
| `frontend/app/layout.tsx` | Root layout, fonts, metadata |
| `frontend/app/page.tsx` | Redirect to /analyse |
| `frontend/app/globals.css` | Tailwind imports + custom CSS |
| `frontend/app/analyse/page.tsx` | Main analysis page |
| `frontend/components/ContentInput/index.tsx` | Tabbed container |
| `frontend/components/ContentInput/TextInput.tsx` | Text textarea + counter |
| `frontend/components/ContentInput/ImageUpload.tsx` | Drag-and-drop image |
| `frontend/components/ContentInput/VideoUpload.tsx` | Drag-and-drop video |
| `frontend/components/PlatformSelector.tsx` | Platform pill buttons |
| `frontend/components/ViralScore.tsx` | Animated circular gauge |
| `frontend/components/DimensionChart.tsx` | Recharts radar chart |
| `frontend/components/Suggestions.tsx` | Strengths/weaknesses/suggestion cards |
| `frontend/components/KeyframeTimeline.tsx` | Video keyframe strip |
| `frontend/components/ImageInsights.tsx` | Image analysis view |
| `frontend/components/RecommendationsBar.tsx` | Hashtags, timing, tips |
| `frontend/lib/api.ts` | Typed API client |
| `frontend/lib/types.ts` | TypeScript interfaces |

### Root

| File | Responsibility |
|---|---|
| `docker-compose.yml` | Local dev orchestration |

---

### Task 1: Backend scaffolding, config, and schemas

**Files:**
- Create: `backend/app/__init__.py`, `backend/app/main.py`, `backend/app/config.py`, `backend/app/models/__init__.py`, `backend/app/models/schemas.py`, `backend/app/routers/__init__.py`, `backend/app/routers/analyse.py` (stub), `backend/app/services/__init__.py`, `backend/requirements.txt`, `backend/.env.example`, `backend/Dockerfile`, `tests/conftest.py`, `tests/test_api.py`

**Interfaces:**
- Produces: `Settings` class (consumed by all services), all Pydantic models (`AnalyseRequest`, `AnalyseResponse`, `QuickAnalyseRequest`, `QuickAnalyseResponse`, `NlpFeatures`, `CvFeatures`, `VideoFeatures`, `DimensionScore`, `Suggestion`), FastAPI app instance with health endpoint.

- [ ] **Step 1: Create requirements.txt**

```
# backend/requirements.txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
python-multipart==0.0.9
pydantic==2.9.0
pydantic-settings==2.5.0

# NLP
textstat==0.7.4
vaderSentiment==3.3.2
nltk==3.9.1

# Image processing
Pillow==10.4.0
opencv-python-headless==4.10.0.84
pytesseract==0.3.13
scikit-learn==1.5.2
numpy==1.26.4

# Video
ffmpeg-python==0.2.0

# AI APIs
google-generativeai==0.8.0
groq==0.11.0

# Database
supabase==2.7.0

# Testing
pytest==8.3.0
pytest-asyncio==0.24.0
httpx==0.27.0
```

- [ ] **Step 2: Create .env.example**

```
# backend/.env.example
GEMINI_API_KEY=your-gemini-api-key
GROQ_API_KEY=your-groq-api-key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
CORS_ORIGINS=http://localhost:3000
MAX_VIDEO_DURATION_SECONDS=60
MAX_IMAGE_SIZE_MB=10
MAX_VIDEO_SIZE_MB=50
```

- [ ] **Step 3: Create config.py**

```python
# backend/app/config.py
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
```

- [ ] **Step 4: Create Pydantic schemas**

```python
# backend/app/models/__init__.py
# (empty)

# backend/app/models/schemas.py
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
```

- [ ] **Step 5: Create FastAPI app with health endpoint**

```python
# backend/app/__init__.py
# (empty)

# backend/app/services/__init__.py
# (empty)

# backend/app/routers/__init__.py
# (empty)

# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import analyse

app = FastAPI(title="Viralify API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyse.router, prefix="/api")
```

```python
# backend/app/routers/analyse.py
from fastapi import APIRouter

from app.models.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse()
```

- [ ] **Step 6: Create Dockerfile**

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "import nltk; nltk.download('vader_lexicon', download_dir='/usr/local/nltk_data')"

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 7: Write health endpoint test**

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
```

```python
# tests/test_api.py
import pytest


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"
```

- [ ] **Step 8: Run tests**

```bash
cd backend
pip install -r requirements.txt
pytest tests/test_api.py -v
```

Expected: 1 passed.

- [ ] **Step 9: Commit**

```bash
git add backend/ tests/
git commit -m "feat: backend scaffolding with config, schemas, and health endpoint"
```

---

### Task 2: Text NLP analyzer

**Files:**
- Create: `backend/app/services/nlp_analyzer.py`, `tests/test_nlp_analyzer.py`

**Interfaces:**
- Consumes: `NlpFeatures` model from `app.models.schemas`
- Produces: `analyse_text(text: str, platform: str) -> NlpFeatures` function, `compute_quick_score(features: NlpFeatures) -> int` function

- [ ] **Step 1: Write failing tests for NLP analyzer**

```python
# tests/test_nlp_analyzer.py
import pytest

from app.services.nlp_analyzer import analyse_text, compute_quick_score


class TestAnalyseText:
    def test_basic_text_returns_nlp_features(self):
        text = "This is a shocking revelation that will change everything you know about AI!"
        features = analyse_text(text, "twitter")
        assert features.word_count == 14
        assert features.char_count == len(text)
        assert features.sentence_count >= 1
        assert 0 <= features.flesch_reading_ease <= 100
        assert features.vader_compound != 0.0
        assert features.has_curiosity_gap is True
        assert features.power_word_count >= 1
        assert "shocking" in features.power_words_found

    def test_question_detection(self):
        text = "Did you know this? What about that? Here are the facts."
        features = analyse_text(text, "general")
        assert features.has_questions is True
        assert features.question_count == 2

    def test_hashtag_extraction(self):
        text = "Great tips for #marketing and #growth today"
        features = analyse_text(text, "twitter")
        assert features.hashtag_count == 2
        assert "#marketing" in features.hashtags
        assert "#growth" in features.hashtags

    def test_emoji_detection(self):
        text = "This is amazing! 🔥🚀 Check it out"
        features = analyse_text(text, "instagram")
        assert features.emoji_count == 2

    def test_platform_fit_twitter_optimal(self):
        text = "Short punchy tweet #viral"
        features = analyse_text(text, "twitter")
        assert 0 <= features.length_fit_score <= 100
        assert 0 <= features.hashtag_fit_score <= 100

    def test_platform_fit_linkedin_long(self):
        text = "A " * 700  # ~1400 chars, within LinkedIn optimal
        features = analyse_text(text, "linkedin")
        assert features.length_fit_score > 50

    def test_cta_detection(self):
        text = "Follow me for more tips and share this with your friends!"
        features = analyse_text(text, "instagram")
        assert features.has_cta is True

    def test_controversy_markers(self):
        text = "Unpopular opinion: this is the worst take I've seen"
        features = analyse_text(text, "twitter")
        assert features.has_controversy is True

    def test_personal_story_markers(self):
        text = "I learned something incredible from my experience last year"
        features = analyse_text(text, "linkedin")
        assert features.has_personal_story is True

    def test_urgency_markers(self):
        text = "Breaking news just happened now! Limited time offer"
        features = analyse_text(text, "twitter")
        assert features.has_urgency is True

    def test_list_format_detection(self):
        text = "1. First thing\n2. Second thing\n3. Third thing"
        features = analyse_text(text, "linkedin")
        assert features.has_list_format is True

    def test_first_line_extraction(self):
        text = "This is the hook line.\nThis is the body."
        features = analyse_text(text, "twitter")
        assert features.first_line == "This is the hook line."


class TestQuickScore:
    def test_quick_score_range(self):
        text = "Check out this amazing hack for productivity! #tips"
        features = analyse_text(text, "twitter")
        score = compute_quick_score(features)
        assert 0 <= score <= 100

    def test_high_engagement_text_scores_higher(self):
        boring = "The meeting is at 3pm."
        engaging = "🔥 Shocking secret hack that will BLOW YOUR MIND! Share this now! #viral #trending"
        boring_score = compute_quick_score(analyse_text(boring, "twitter"))
        engaging_score = compute_quick_score(analyse_text(engaging, "twitter"))
        assert engaging_score > boring_score
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd backend
pytest tests/test_nlp_analyzer.py -v
```

Expected: FAIL with `ModuleNotFoundError: No module named 'app.services.nlp_analyzer'`

- [ ] **Step 3: Implement NLP analyzer**

```python
# backend/app/services/nlp_analyzer.py
import re
import math

import textstat
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from app.models.schemas import NlpFeatures

_vader = SentimentIntensityAnalyzer()

POWER_WORDS = [
    "secret", "shocking", "hack", "proven", "ultimate", "exclusive",
    "breaking", "urgent", "amazing", "incredible", "unbelievable",
    "revolutionary", "guaranteed", "instant", "free", "new", "discover",
    "revealed", "warning", "alert", "banned", "controversial", "hidden",
    "insider", "limited", "rare", "surprising", "unexpected", "unknown",
    "unleash",
]

CTA_PATTERNS = re.compile(
    r"\b(share|tag|follow|subscribe|retweet|like|comment|save|click|"
    r"check out|sign up|join|dm me|link in bio|swipe)\b",
    re.IGNORECASE,
)

CONTROVERSY_PATTERNS = re.compile(
    r"\b(unpopular opinion|hot take|change my mind|fight me|"
    r"controversial|disagree|debate)\b",
    re.IGNORECASE,
)

PERSONAL_STORY_PATTERNS = re.compile(
    r"\b(i learned|my experience|true story|personal story|"
    r"i discovered|happened to me|my journey|i realized|i used to)\b",
    re.IGNORECASE,
)

CURIOSITY_GAP_PATTERNS = re.compile(
    r"\b(you won't believe|here's why|turns out|the reason|"
    r"what happened next|the truth about|nobody tells you|"
    r"little known|most people don't)\b",
    re.IGNORECASE,
)

SOCIAL_PROOF_PATTERNS = re.compile(
    r"\b(went viral|trending|everyone|millions|thousands|"
    r"most popular|best selling|number one|top rated)\b",
    re.IGNORECASE,
)

URGENCY_PATTERNS = re.compile(
    r"\b(now|limited|breaking|just happened|hurry|last chance|"
    r"don't miss|act fast|ending soon|today only)\b",
    re.IGNORECASE,
)

EMOJI_PATTERN = re.compile(
    r"[\U0001f600-\U0001f64f\U0001f300-\U0001f5ff\U0001f680-\U0001f6ff"
    r"\U0001f1e0-\U0001f1ff\U00002702-\U000027b0\U0001f900-\U0001f9ff"
    r"\U0001fa00-\U0001fa6f\U0001fa70-\U0001faff\U00002600-\U000026ff"
    r"\U0000fe0f]"
)

HASHTAG_PATTERN = re.compile(r"#\w+")
MENTION_PATTERN = re.compile(r"@\w+")
URL_PATTERN = re.compile(r"https?://\S+")
NUMBER_PATTERN = re.compile(r"\b\d+[\d,.]*%?\b")

PLATFORM_OPTIMAL = {
    "twitter": {"char_min": 71, "char_max": 280, "hashtag_min": 1, "hashtag_max": 2},
    "linkedin": {"char_min": 1300, "char_max": 2000, "hashtag_min": 3, "hashtag_max": 5},
    "instagram": {"char_min": 138, "char_max": 150, "hashtag_min": 5, "hashtag_max": 10},
    "tiktok": {"char_min": 80, "char_max": 150, "hashtag_min": 3, "hashtag_max": 5},
    "reddit": {"char_min": 100, "char_max": 800, "hashtag_min": 0, "hashtag_max": 0},
    "youtube": {"char_min": 200, "char_max": 500, "hashtag_min": 2, "hashtag_max": 4},
    "blog": {"char_min": 7500, "char_max": 12500, "hashtag_min": 0, "hashtag_max": 0},
    "general": {"char_min": 100, "char_max": 1000, "hashtag_min": 0, "hashtag_max": 3},
}


def _compute_length_fit(char_count: int, platform: str) -> float:
    opts = PLATFORM_OPTIMAL.get(platform, PLATFORM_OPTIMAL["general"])
    cmin, cmax = opts["char_min"], opts["char_max"]
    if cmin <= char_count <= cmax:
        return 100.0
    if char_count < cmin:
        return max(0.0, 100.0 * char_count / cmin)
    return max(0.0, 100.0 - 100.0 * (char_count - cmax) / cmax)


def _compute_hashtag_fit(hashtag_count: int, platform: str) -> float:
    opts = PLATFORM_OPTIMAL.get(platform, PLATFORM_OPTIMAL["general"])
    hmin, hmax = opts["hashtag_min"], opts["hashtag_max"]
    if hmin == 0 and hmax == 0:
        return 100.0 if hashtag_count == 0 else max(0.0, 100.0 - hashtag_count * 20)
    if hmin <= hashtag_count <= hmax:
        return 100.0
    if hashtag_count < hmin:
        return max(0.0, 100.0 * hashtag_count / hmin) if hmin > 0 else 100.0
    return max(0.0, 100.0 - 100.0 * (hashtag_count - hmax) / hmax)


def _mass_appeal_score(grade_level: float) -> float:
    """Peaks at grade 6-8 (sweet spot for mass appeal)."""
    ideal = 7.0
    distance = abs(grade_level - ideal)
    return max(0.0, min(100.0, 100.0 - distance * 10))


def analyse_text(text: str, platform: str) -> NlpFeatures:
    words = text.split()
    word_count = len(words)
    char_count = len(text)
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
    sentence_count = max(1, len(sentences))
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    paragraph_count = max(1, len(paragraphs))

    avg_sentence_length = word_count / sentence_count if sentence_count else 0
    avg_word_length = (
        sum(len(w) for w in words) / word_count if word_count else 0
    )

    # Readability
    flesch_re = textstat.flesch_reading_ease(text) if word_count > 0 else 0
    flesch_kincaid = textstat.flesch_kincaid_grade(text) if word_count > 0 else 0
    gunning_fog = textstat.gunning_fog(text) if word_count > 0 else 0
    smog = textstat.smog_index(text) if word_count > 0 else 0
    reading_time = word_count / 250 * 60  # seconds at 250 WPM

    # Sentiment
    vader_scores = _vader.polarity_scores(text)
    compound = vader_scores["compound"]
    abs_compound = abs(compound)
    if abs_compound >= 0.6:
        arousal_level = "high"
    elif abs_compound >= 0.3:
        arousal_level = "medium"
    else:
        arousal_level = "low"
    arousal_score = min(100.0, abs_compound * 100 / 0.8)

    if compound >= 0.05:
        dominant_tone = "positive"
    elif compound <= -0.05:
        dominant_tone = "negative"
    else:
        dominant_tone = "neutral"

    # Structure
    questions = re.findall(r"\?", text)
    question_count = len(questions)
    has_questions = question_count > 0
    has_list_format = bool(re.search(r"^\s*[\d\-\*\•]\s*\S", text, re.MULTILINE))

    emojis = EMOJI_PATTERN.findall(text)
    emoji_count = len(emojis)

    hashtags = HASHTAG_PATTERN.findall(text)
    hashtag_count = len(hashtags)

    mentions = MENTION_PATTERN.findall(text)
    mention_count = len(mentions)

    urls = URL_PATTERN.findall(text)
    url_count = len(urls)

    caps_words = [w for w in words if w.isupper() and len(w) > 1]
    has_caps_emphasis = len(caps_words) >= 1

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    first_line = lines[0] if lines else ""

    # Engagement signals
    text_lower = text.lower()
    found_power_words = [w for w in POWER_WORDS if w in text_lower]
    power_word_count = len(found_power_words)

    has_cta = bool(CTA_PATTERNS.search(text))
    has_numbers = bool(NUMBER_PATTERN.search(text))
    has_controversy = bool(CONTROVERSY_PATTERNS.search(text))
    has_personal_story = bool(PERSONAL_STORY_PATTERNS.search(text))
    has_curiosity_gap = bool(CURIOSITY_GAP_PATTERNS.search(text))
    has_social_proof = bool(SOCIAL_PROOF_PATTERNS.search(text))
    has_urgency = bool(URGENCY_PATTERNS.search(text))

    # Platform fit
    length_fit = _compute_length_fit(char_count, platform)
    hashtag_fit = _compute_hashtag_fit(hashtag_count, platform)
    platform_fit = (length_fit + hashtag_fit) / 2

    return NlpFeatures(
        flesch_reading_ease=round(flesch_re, 1),
        flesch_kincaid_grade=round(flesch_kincaid, 1),
        gunning_fog=round(gunning_fog, 1),
        smog_index=round(smog, 1),
        reading_time_seconds=round(reading_time, 1),
        mass_appeal_score=round(_mass_appeal_score(flesch_kincaid), 1),
        vader_compound=round(compound, 4),
        vader_positive=round(vader_scores["pos"], 4),
        vader_negative=round(vader_scores["neg"], 4),
        vader_neutral=round(vader_scores["neu"], 4),
        arousal_level=arousal_level,
        arousal_score=round(arousal_score, 1),
        dominant_tone=dominant_tone,
        word_count=word_count,
        char_count=char_count,
        sentence_count=sentence_count,
        paragraph_count=paragraph_count,
        avg_sentence_length=round(avg_sentence_length, 1),
        avg_word_length=round(avg_word_length, 1),
        has_questions=has_questions,
        question_count=question_count,
        has_list_format=has_list_format,
        emoji_count=emoji_count,
        hashtag_count=hashtag_count,
        hashtags=hashtags,
        mention_count=mention_count,
        url_count=url_count,
        has_caps_emphasis=has_caps_emphasis,
        first_line=first_line,
        power_word_count=power_word_count,
        power_words_found=found_power_words,
        has_cta=has_cta,
        has_numbers=has_numbers,
        has_controversy=has_controversy,
        has_personal_story=has_personal_story,
        has_curiosity_gap=has_curiosity_gap,
        has_social_proof=has_social_proof,
        has_urgency=has_urgency,
        length_fit_score=round(length_fit, 1),
        hashtag_fit_score=round(hashtag_fit, 1),
        platform_fit_score=round(platform_fit, 1),
    )


def compute_quick_score(features: NlpFeatures) -> int:
    """Compute a 0-100 quick score from NLP features alone."""
    score = 50.0  # baseline

    # Readability bonus (mass appeal sweet spot)
    score += (features.mass_appeal_score - 50) * 0.15

    # Sentiment arousal bonus
    score += features.arousal_score * 0.1

    # Engagement signals (each adds up to 3-5 points)
    if features.has_cta:
        score += 3
    if features.has_curiosity_gap:
        score += 5
    if features.has_controversy:
        score += 4
    if features.has_personal_story:
        score += 3
    if features.has_social_proof:
        score += 3
    if features.has_urgency:
        score += 3
    if features.has_questions:
        score += 2
    if features.has_numbers:
        score += 2
    if features.emoji_count > 0:
        score += min(3, features.emoji_count)

    # Power words
    score += min(5, features.power_word_count * 1.5)

    # Platform fit
    score += (features.platform_fit_score - 50) * 0.2

    return max(0, min(100, round(score)))
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd backend
python -c "import nltk; nltk.download('vader_lexicon')"
pytest tests/test_nlp_analyzer.py -v
```

Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/nlp_analyzer.py tests/test_nlp_analyzer.py
git commit -m "feat: text NLP analyzer with readability, sentiment, engagement signals"
```

---

### Task 3: Gemini analyzer (text + vision)

**Files:**
- Create: `backend/app/services/gemini_analyzer.py`, `tests/test_gemini_analyzer.py`

**Interfaces:**
- Consumes: `NlpFeatures`, `CvFeatures`, `VideoFeatures`, `AnalyseResponse` from schemas. `settings.gemini_api_key` from config.
- Produces: `analyse_with_gemini(content_type: str, platform: str, text_content: str | None, image_bytes: bytes | None, keyframe_images: list[bytes] | None, nlp_features: NlpFeatures | None, cv_features: CvFeatures | None, video_features: VideoFeatures | None) -> dict` function. Returns the parsed Gemini JSON response as a dict matching the AnalyseResponse shape.

- [ ] **Step 1: Write failing tests (mocked Gemini)**

```python
# tests/test_gemini_analyzer.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_gemini_analyzer.py -v
```

Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement Gemini analyzer**

```python
# backend/app/services/gemini_analyzer.py
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
        "gemini-2.5-flash",
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_gemini_analyzer.py -v
```

Expected: All tests pass (Gemini calls are mocked).

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/gemini_analyzer.py tests/test_gemini_analyzer.py
git commit -m "feat: Gemini analyzer with STEPPS prompt for text, image, and video"
```

---

### Task 4: Image analyzer (local CV features)

**Files:**
- Create: `backend/app/services/image_analyzer.py`, `tests/test_image_analyzer.py`

**Interfaces:**
- Consumes: `CvFeatures` model from schemas
- Produces: `analyse_image(image_bytes: bytes) -> CvFeatures` function

- [ ] **Step 1: Write failing tests**

```python
# tests/test_image_analyzer.py
import io
import pytest
from PIL import Image
import numpy as np

from app.services.image_analyzer import analyse_image


def _make_test_image(width=200, height=200, color=(255, 0, 0)) -> bytes:
    """Create a solid-color test image as bytes."""
    img = Image.new("RGB", (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _make_gradient_image(width=300, height=300) -> bytes:
    """Create a gradient test image with varied brightness."""
    arr = np.zeros((height, width, 3), dtype=np.uint8)
    for y in range(height):
        val = int(255 * y / height)
        arr[y, :] = [val, val, val]
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


class TestAnalyseImage:
    def test_dimensions(self):
        image_bytes = _make_test_image(400, 300)
        features = analyse_image(image_bytes)
        assert features.width == 400
        assert features.height == 300
        assert abs(features.aspect_ratio - 400 / 300) < 0.01

    def test_brightness_solid_white(self):
        image_bytes = _make_test_image(100, 100, color=(255, 255, 255))
        features = analyse_image(image_bytes)
        assert features.brightness_score > 90

    def test_brightness_solid_black(self):
        image_bytes = _make_test_image(100, 100, color=(0, 0, 0))
        features = analyse_image(image_bytes)
        assert features.brightness_score < 10

    def test_contrast_gradient(self):
        image_bytes = _make_gradient_image()
        features = analyse_image(image_bytes)
        assert features.contrast_score > 20  # gradient has contrast

    def test_contrast_solid(self):
        image_bytes = _make_test_image(100, 100, color=(128, 128, 128))
        features = analyse_image(image_bytes)
        assert features.contrast_score < 10  # solid has near-zero contrast

    def test_dominant_colors_returned(self):
        image_bytes = _make_test_image(100, 100, color=(255, 0, 0))
        features = analyse_image(image_bytes)
        assert len(features.dominant_colors) >= 1
        # dominant color should be close to red
        r, g, b = features.dominant_colors[0]
        assert r > 200

    def test_face_count_no_faces(self):
        image_bytes = _make_test_image(200, 200)
        features = analyse_image(image_bytes)
        assert features.face_count == 0

    def test_composition_score_range(self):
        image_bytes = _make_gradient_image()
        features = analyse_image(image_bytes)
        assert 0 <= features.composition_score <= 100
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_image_analyzer.py -v
```

Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement image analyzer**

```python
# backend/app/services/image_analyzer.py
import io

import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans

from app.models.schemas import CvFeatures


def _get_dominant_colors(image: Image.Image, n_colors: int = 5) -> list[list[int]]:
    """Extract dominant colors via k-means clustering on downsampled pixels."""
    small = image.resize((100, 100))
    pixels = np.array(small).reshape(-1, 3)
    n_colors = min(n_colors, len(np.unique(pixels, axis=0)))
    if n_colors < 1:
        return [[0, 0, 0]]
    kmeans = KMeans(n_clusters=n_colors, n_init=5, random_state=42)
    kmeans.fit(pixels)
    colors = kmeans.cluster_centers_.astype(int).tolist()
    # Sort by frequency (cluster size)
    labels, counts = np.unique(kmeans.labels_, return_counts=True)
    sorted_idx = np.argsort(-counts)
    return [colors[i] for i in sorted_idx]


def _brightness_score(image: Image.Image) -> float:
    """Mean luminance of grayscale conversion, scaled to 0-100."""
    gray = image.convert("L")
    arr = np.array(gray)
    return float(arr.mean() / 255.0 * 100)


def _contrast_score(image: Image.Image) -> float:
    """Standard deviation of luminance, scaled to 0-100."""
    gray = image.convert("L")
    arr = np.array(gray)
    std = float(arr.std())
    return min(100.0, std / 128.0 * 100)  # 128 is max std for 0-255


def _face_count(cv_image: np.ndarray) -> int:
    """Count faces using OpenCV Haar cascade."""
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return len(faces)


def _detect_text(image: Image.Image) -> tuple[bool, str]:
    """Detect text on image via pytesseract. Returns (has_text, detected_text)."""
    try:
        import pytesseract
        text = pytesseract.image_to_string(image, timeout=5).strip()
        has_text = len(text) > 5  # filter noise
        return has_text, text if has_text else ""
    except Exception:
        return False, ""


def _composition_score(image: Image.Image) -> float:
    """Rule-of-thirds approximation. Checks if visual interest
    (high-variance regions) falls near the 4 intersection points."""
    gray = np.array(image.convert("L").resize((150, 150)), dtype=float)
    h, w = gray.shape

    # Compute local variance in 15x15 patches
    patch_size = 15
    interest_map = np.zeros((h // patch_size, w // patch_size))
    for i in range(interest_map.shape[0]):
        for j in range(interest_map.shape[1]):
            patch = gray[
                i * patch_size : (i + 1) * patch_size,
                j * patch_size : (j + 1) * patch_size,
            ]
            interest_map[i, j] = patch.std()

    if interest_map.max() == 0:
        return 50.0  # uniform image

    interest_map = interest_map / interest_map.max()

    # Rule-of-thirds intersection points (relative positions)
    thirds = [(1 / 3, 1 / 3), (2 / 3, 1 / 3), (1 / 3, 2 / 3), (2 / 3, 2 / 3)]
    score = 0.0
    ih, iw = interest_map.shape
    for ry, rx in thirds:
        y, x = int(ry * ih), int(rx * iw)
        y = min(y, ih - 1)
        x = min(x, iw - 1)
        # Average interest in a small neighborhood
        y_start, y_end = max(0, y - 1), min(ih, y + 2)
        x_start, x_end = max(0, x - 1), min(iw, x + 2)
        region = interest_map[y_start:y_end, x_start:x_end]
        score += region.mean()

    # Normalize: max possible is 4.0 (all interest at intersection points)
    return min(100.0, score / 4.0 * 100)


def analyse_image(image_bytes: bytes) -> CvFeatures:
    """Extract local CV features from image bytes."""
    pil_image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    width, height = pil_image.size

    # OpenCV format for face detection
    cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    has_text, detected_text = _detect_text(pil_image)

    return CvFeatures(
        width=width,
        height=height,
        aspect_ratio=round(width / height, 3) if height > 0 else 0,
        brightness_score=round(_brightness_score(pil_image), 1),
        contrast_score=round(_contrast_score(pil_image), 1),
        dominant_colors=_get_dominant_colors(pil_image),
        face_count=_face_count(cv_image),
        has_text_overlay=has_text,
        detected_text=detected_text,
        composition_score=round(_composition_score(pil_image), 1),
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_image_analyzer.py -v
```

Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add backend/app/services/image_analyzer.py tests/test_image_analyzer.py
git commit -m "feat: image analyzer with color, brightness, faces, composition"
```

---

### Task 5: Video analyzer + Whisper client

**Files:**
- Create: `backend/app/services/whisper_client.py`, `backend/app/services/video_analyzer.py`, `tests/test_video_analyzer.py`

**Interfaces:**
- Consumes: `VideoFeatures`, `CvFeatures`, `NlpFeatures` from schemas. `analyse_image(bytes) -> CvFeatures` from image_analyzer. `analyse_text(str, str) -> NlpFeatures` from nlp_analyzer. `settings.groq_api_key` from config.
- Produces: `transcribe_audio(audio_path: str) -> str` function from whisper_client. `analyse_video(video_bytes: bytes, platform: str) -> tuple[VideoFeatures, list[bytes]]` function from video_analyzer (returns features and keyframe image bytes for Gemini).

- [ ] **Step 1: Write failing tests**

```python
# tests/test_video_analyzer.py
import io
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from app.services.whisper_client import transcribe_audio
from app.services.video_analyzer import (
    extract_keyframes,
    extract_audio,
    select_top_keyframes,
    analyse_video,
)


class TestWhisperClient:
    @patch("app.services.whisper_client.Groq")
    def test_transcribe_returns_text(self, mock_groq_cls):
        mock_client = MagicMock()
        mock_groq_cls.return_value = mock_client
        mock_transcription = MagicMock()
        mock_transcription.text = "Hello everyone welcome to my channel"
        mock_client.audio.transcriptions.create.return_value = mock_transcription

        result = transcribe_audio("/tmp/test_audio.wav")
        assert result == "Hello everyone welcome to my channel"

    @patch("app.services.whisper_client.Groq")
    def test_transcribe_failure_returns_empty(self, mock_groq_cls):
        mock_client = MagicMock()
        mock_groq_cls.return_value = mock_client
        mock_client.audio.transcriptions.create.side_effect = Exception("API Error")

        result = transcribe_audio("/tmp/test_audio.wav")
        assert result == ""


class TestKeyframeSelection:
    def test_select_top_keyframes_reduces_count(self):
        # Create 5 fake keyframe images of different brightness
        frames = []
        for brightness in [50, 100, 150, 200, 250]:
            import numpy as np
            from PIL import Image
            arr = np.full((100, 100, 3), brightness, dtype=np.uint8)
            img = Image.fromarray(arr)
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            frames.append(buf.getvalue())

        top_3 = select_top_keyframes(frames, n=3)
        assert len(top_3) == 3

    def test_select_returns_all_if_fewer_than_n(self):
        frames = [b"frame1", b"frame2"]
        result = select_top_keyframes(frames, n=3)
        assert len(result) == 2
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_video_analyzer.py -v
```

Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Implement Whisper client**

```python
# backend/app/services/whisper_client.py
from groq import Groq

from app.config import settings


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file using Groq Whisper. Returns empty string on failure."""
    try:
        client = Groq(api_key=settings.groq_api_key)
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(audio_path, audio_file.read()),
                model="whisper-large-v3",
                response_format="text",
            )
        return transcription.text if hasattr(transcription, "text") else str(transcription)
    except Exception:
        return ""
```

- [ ] **Step 4: Implement video analyzer**

```python
# backend/app/services/video_analyzer.py
import io
import os
import tempfile
import subprocess

import numpy as np
from PIL import Image

from app.models.schemas import VideoFeatures, CvFeatures, NlpFeatures
from app.services.image_analyzer import analyse_image
from app.services.nlp_analyzer import analyse_text
from app.services.whisper_client import transcribe_audio


def _get_video_duration(video_path: str) -> float:
    """Get video duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", video_path,
            ],
            capture_output=True, text=True, timeout=10,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def extract_keyframes(video_path: str, n_frames: int = 5) -> list[bytes]:
    """Extract n evenly-spaced keyframes from video as JPEG bytes."""
    duration = _get_video_duration(video_path)
    if duration <= 0:
        return []

    frames = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(n_frames):
            timestamp = duration * (i + 0.5) / n_frames  # center of each segment
            output_path = os.path.join(tmpdir, f"frame_{i}.jpg")
            try:
                subprocess.run(
                    [
                        "ffmpeg", "-ss", str(timestamp), "-i", video_path,
                        "-frames:v", "1", "-q:v", "2", output_path,
                        "-y", "-loglevel", "quiet",
                    ],
                    timeout=10, check=True,
                )
                with open(output_path, "rb") as f:
                    frames.append(f.read())
            except Exception:
                continue
    return frames


def extract_audio(video_path: str) -> str:
    """Extract audio from video as WAV file. Returns path to WAV or empty string."""
    try:
        audio_path = video_path + ".wav"
        subprocess.run(
            [
                "ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le",
                "-ar", "16000", "-ac", "1", audio_path,
                "-y", "-loglevel", "quiet",
            ],
            timeout=30, check=True,
        )
        return audio_path
    except Exception:
        return ""


def select_top_keyframes(frames: list[bytes], n: int = 3) -> list[bytes]:
    """Select the n most visually diverse keyframes by histogram distance."""
    if len(frames) <= n:
        return frames

    histograms = []
    for frame_bytes in frames:
        try:
            img = Image.open(io.BytesIO(frame_bytes)).convert("L")
            arr = np.array(img)
            hist, _ = np.histogram(arr.flatten(), bins=64, range=(0, 256))
            hist = hist.astype(float) / hist.sum()
            histograms.append(hist)
        except Exception:
            histograms.append(np.zeros(64))

    # Compute pairwise distances to mean histogram
    mean_hist = np.mean(histograms, axis=0)
    distances = [np.sum(np.abs(h - mean_hist)) for h in histograms]

    # Pick n frames with highest variance from mean (most distinctive)
    sorted_indices = sorted(range(len(distances)), key=lambda i: -distances[i])
    selected = sorted(sorted_indices[:n])  # maintain temporal order
    return [frames[i] for i in selected]


def analyse_video(video_bytes: bytes, platform: str) -> tuple[VideoFeatures, list[bytes]]:
    """Full video analysis pipeline. Returns (features, keyframe_bytes_for_gemini)."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(video_bytes)
        video_path = tmp.name

    try:
        duration = _get_video_duration(video_path)

        # Step 1: Extract keyframes
        n_frames = 5 if duration >= 3 else max(1, int(duration))
        all_frames = extract_keyframes(video_path, n_frames)

        # Step 2: Extract and transcribe audio
        audio_path = extract_audio(video_path)
        transcript = ""
        has_audio = False
        if audio_path and os.path.exists(audio_path):
            has_audio = os.path.getsize(audio_path) > 1000  # >1KB = has real audio
            if has_audio:
                transcript = transcribe_audio(audio_path)
            try:
                os.unlink(audio_path)
            except OSError:
                pass

        # Step 3: Analyse each keyframe with image pipeline
        keyframe_cv_features = []
        for frame_bytes in all_frames:
            try:
                cv_feat = analyse_image(frame_bytes)
                keyframe_cv_features.append(cv_feat)
            except Exception:
                pass

        # Step 4: Analyse transcript with text pipeline
        transcript_nlp = None
        if transcript:
            transcript_nlp = analyse_text(transcript, platform)

        # Select top 3 for Gemini
        top_frames = select_top_keyframes(all_frames, n=3)

        features = VideoFeatures(
            duration_seconds=round(duration, 1),
            keyframe_count=len(all_frames),
            transcript=transcript,
            has_audio=has_audio,
            keyframe_cv_features=keyframe_cv_features,
            transcript_nlp_features=transcript_nlp,
        )

        return features, top_frames
    finally:
        try:
            os.unlink(video_path)
        except OSError:
            pass
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_video_analyzer.py -v
```

Expected: All tests pass (Groq calls are mocked, FFmpeg tests are unit-level).

- [ ] **Step 6: Commit**

```bash
git add backend/app/services/whisper_client.py backend/app/services/video_analyzer.py tests/test_video_analyzer.py
git commit -m "feat: video analyzer with FFmpeg keyframes, Groq Whisper, pipeline orchestration"
```

---

### Task 6: API router + database service

**Files:**
- Modify: `backend/app/routers/analyse.py` (replace stub with full implementation)
- Create: `backend/app/services/database.py`, `backend/supabase_migration.sql`
- Modify: `tests/test_api.py` (add endpoint tests)

**Interfaces:**
- Consumes: All services (`nlp_analyzer.analyse_text`, `nlp_analyzer.compute_quick_score`, `image_analyzer.analyse_image`, `video_analyzer.analyse_video`, `gemini_analyzer.analyse_with_gemini`), all schemas, `settings` from config.
- Produces: `POST /api/analyse`, `POST /api/analyse/quick`, `GET /api/health` HTTP endpoints. `save_analysis(data: dict) -> None` fire-and-forget DB function.

- [ ] **Step 1: Create database service**

```python
# backend/app/services/database.py
import asyncio
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
```

- [ ] **Step 2: Create Supabase migration**

```sql
-- backend/supabase_migration.sql

CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    name TEXT,
    plan TEXT DEFAULT 'free',
    analyses_today INT DEFAULT 0,
    analyses_reset_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id),
    content_type TEXT NOT NULL DEFAULT 'text',
    content_text TEXT,
    platform TEXT NOT NULL DEFAULT 'general',
    overall_score INT,
    quick_score INT,
    dimension_scores JSONB DEFAULT '{}',
    nlp_features JSONB DEFAULT '{}',
    cv_features JSONB DEFAULT '{}',
    video_features JSONB DEFAULT '{}',
    suggestions JSONB DEFAULT '[]',
    gemini_response JSONB DEFAULT '{}',
    media_metadata JSONB DEFAULT '{}',
    processing_time_ms INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analyses(id),
    actually_went_viral BOOLEAN DEFAULT FALSE,
    actual_engagement JSONB DEFAULT '{}',
    reported_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON analyses(created_at);
CREATE INDEX IF NOT EXISTS idx_analyses_overall_score ON analyses(overall_score);
CREATE INDEX IF NOT EXISTS idx_analyses_content_type ON analyses(content_type);
CREATE INDEX IF NOT EXISTS idx_feedback_analysis_id ON feedback(analysis_id);

ALTER TABLE analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

-- Allow anonymous inserts (no auth for MVP)
CREATE POLICY "Allow anonymous inserts" ON analyses FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anonymous reads" ON analyses FOR SELECT USING (true);
CREATE POLICY "Allow anonymous feedback" ON feedback FOR INSERT WITH CHECK (true);
```

- [ ] **Step 3: Implement full API router**

```python
# backend/app/routers/analyse.py
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

    # Phase 2: Gemini analysis
    try:
        gemini_result = analyse_with_gemini(
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
            gemini_result = analyse_with_gemini(
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

    from app.models.schemas import DimensionScores, DimensionScore, Suggestion

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
```

- [ ] **Step 4: Add API endpoint tests**

```python
# Append to tests/test_api.py
import io
from unittest.mock import patch, MagicMock

import pytest
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
```

- [ ] **Step 5: Run all tests**

```bash
cd backend
pytest tests/ -v
```

Expected: All tests pass.

- [ ] **Step 6: Commit**

```bash
git add backend/app/routers/analyse.py backend/app/services/database.py backend/supabase_migration.sql tests/test_api.py
git commit -m "feat: API endpoints with full analysis pipeline + Supabase persistence"
```

---

### Task 7: Frontend scaffolding, API client, content input, and platform selector

**Files:**
- Create: all frontend files listed in the file map for `frontend/`

**Interfaces:**
- Consumes: Backend API at `NEXT_PUBLIC_API_URL` (endpoints defined in Task 6)
- Produces: Next.js app with content input UI (text/image/video tabs), platform selector, API client, TypeScript types

- [ ] **Step 1: Initialize Next.js project**

```bash
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir=false --import-alias="@/*" --no-eslint
cd frontend
npm install recharts framer-motion lucide-react
```

- [ ] **Step 2: Create TypeScript types**

```typescript
// frontend/lib/types.ts
export type Platform = "twitter" | "linkedin" | "instagram" | "tiktok" | "reddit" | "youtube" | "blog" | "general";
export type ContentType = "text" | "image" | "video";
export type Priority = "high" | "medium" | "low";
export type Confidence = "high" | "medium" | "low";

export interface DimensionScore {
  score: number;
  detail: string;
}

export interface DimensionScores {
  emotional_impact: DimensionScore;
  social_currency: DimensionScore;
  practical_value: DimensionScore;
  narrative_strength: DimensionScore;
  trigger_potential: DimensionScore;
  shareability: DimensionScore;
  platform_fit: DimensionScore;
  hook_quality: DimensionScore;
}

export interface Suggestion {
  text: string;
  priority: Priority;
}

export interface NlpFeatures {
  word_count: number;
  char_count: number;
  sentence_count: number;
  flesch_reading_ease: number;
  vader_compound: number;
  arousal_level: string;
  platform_fit_score: number;
  [key: string]: unknown;
}

export interface CvFeatures {
  width: number;
  height: number;
  aspect_ratio: number;
  brightness_score: number;
  contrast_score: number;
  dominant_colors: number[][];
  face_count: number;
  has_text_overlay: boolean;
  detected_text: string;
  composition_score: number;
}

export interface VideoFeatures {
  duration_seconds: number;
  keyframe_count: number;
  transcript: string;
  has_audio: boolean;
}

export interface AnalyseResponse {
  content_type: ContentType;
  overall_score: number;
  verdict: string;
  quick_score: number | null;
  nlp_features: NlpFeatures | null;
  cv_features: CvFeatures | null;
  video_features: VideoFeatures | null;
  dimension_scores: DimensionScores;
  emotions_detected: string[];
  strengths: string[];
  weaknesses: string[];
  suggestions: Suggestion[];
  rewritten_hook: string | null;
  thumbnail_suggestions: string | null;
  best_posting_times: string[];
  recommended_hashtags: string[];
  confidence: Confidence;
  processing_time_ms: number;
}
```

- [ ] **Step 3: Create API client**

```typescript
// frontend/lib/api.ts
import type { AnalyseResponse, ContentType, Platform } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function analyseContent(params: {
  contentType: ContentType;
  platform: Platform;
  content?: string;
  file?: File;
}): Promise<AnalyseResponse> {
  const formData = new FormData();
  formData.append("content_type", params.contentType);
  formData.append("platform", params.platform);

  if (params.content) {
    formData.append("content", params.content);
  }
  if (params.file) {
    formData.append("file", params.file);
  }

  const resp = await fetch(`${API_URL}/api/analyse`, {
    method: "POST",
    body: formData,
  });

  if (!resp.ok) {
    const error = await resp.json().catch(() => ({ detail: "Analysis failed" }));
    throw new Error(error.detail || `HTTP ${resp.status}`);
  }

  return resp.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const resp = await fetch(`${API_URL}/api/health`);
    return resp.ok;
  } catch {
    return false;
  }
}
```

- [ ] **Step 4: Create .env.local.example**

```
# frontend/.env.local.example
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

- [ ] **Step 5: Create PlatformSelector component**

```tsx
// frontend/components/PlatformSelector.tsx
"use client";

import type { Platform } from "@/lib/types";

const PLATFORMS: { value: Platform; label: string; icon: string }[] = [
  { value: "twitter", label: "Twitter/X", icon: "𝕏" },
  { value: "linkedin", label: "LinkedIn", icon: "in" },
  { value: "instagram", label: "Instagram", icon: "📸" },
  { value: "tiktok", label: "TikTok", icon: "♪" },
  { value: "reddit", label: "Reddit", icon: "⬆" },
  { value: "youtube", label: "YouTube", icon: "▶" },
  { value: "blog", label: "Blog", icon: "✍" },
  { value: "general", label: "General", icon: "🌐" },
];

interface Props {
  selected: Platform;
  onChange: (platform: Platform) => void;
}

export default function PlatformSelector({ selected, onChange }: Props) {
  return (
    <div className="flex flex-wrap gap-2">
      {PLATFORMS.map((p) => (
        <button
          key={p.value}
          onClick={() => onChange(p.value)}
          className={`px-4 py-2 rounded-full text-sm font-medium transition-all
            ${
              selected === p.value
                ? "bg-indigo-600 text-white shadow-lg shadow-indigo-500/25"
                : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white border border-white/10"
            }`}
        >
          <span className="mr-1.5">{p.icon}</span>
          {p.label}
        </button>
      ))}
    </div>
  );
}
```

- [ ] **Step 6: Create ContentInput components**

```tsx
// frontend/components/ContentInput/TextInput.tsx
"use client";

import { useState } from "react";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

export default function TextInput({ value, onChange }: Props) {
  const wordCount = value.trim() ? value.trim().split(/\s+/).length : 0;
  const charCount = value.length;

  return (
    <div className="relative">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Paste your content here — a tweet, LinkedIn post, caption, blog intro, video script..."
        className="w-full h-48 p-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50 transition-all"
      />
      <div className="absolute bottom-3 right-3 flex gap-3 text-xs text-gray-500">
        <span>{wordCount} words</span>
        <span>{charCount} chars</span>
      </div>
    </div>
  );
}
```

```tsx
// frontend/components/ContentInput/ImageUpload.tsx
"use client";

import { useCallback, useState } from "react";
import { Upload, X, Image as ImageIcon } from "lucide-react";

interface Props {
  file: File | null;
  onChange: (file: File | null) => void;
}

export default function ImageUpload({ file, onChange }: Props) {
  const [preview, setPreview] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFile = useCallback(
    (f: File) => {
      if (f.size > 10 * 1024 * 1024) {
        alert("Image must be under 10MB");
        return;
      }
      if (!f.type.startsWith("image/")) {
        alert("Please upload an image file (JPEG, PNG, WebP, GIF)");
        return;
      }
      onChange(f);
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target?.result as string);
      reader.readAsDataURL(f);
    },
    [onChange]
  );

  const clear = () => {
    onChange(null);
    setPreview(null);
  };

  if (preview && file) {
    return (
      <div className="relative rounded-xl overflow-hidden border border-white/10">
        <img src={preview} alt="Preview" className="w-full max-h-64 object-contain bg-black/50" />
        <button
          onClick={clear}
          className="absolute top-2 right-2 p-1.5 bg-black/60 rounded-full hover:bg-black/80 transition"
        >
          <X size={16} className="text-white" />
        </button>
        <div className="p-3 bg-white/5 text-xs text-gray-400">
          {file.name} &middot; {(file.size / 1024 / 1024).toFixed(1)}MB
        </div>
      </div>
    );
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        const f = e.dataTransfer.files[0];
        if (f) handleFile(f);
      }}
      className={`flex flex-col items-center justify-center h-48 border-2 border-dashed rounded-xl transition-all cursor-pointer
        ${dragOver ? "border-indigo-500 bg-indigo-500/10" : "border-white/10 hover:border-white/20 bg-white/5"}`}
    >
      <input
        type="file"
        accept="image/jpeg,image/png,image/webp,image/gif"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) handleFile(f);
        }}
        className="hidden"
        id="image-upload"
      />
      <label htmlFor="image-upload" className="flex flex-col items-center cursor-pointer">
        <ImageIcon size={32} className="text-gray-500 mb-2" />
        <span className="text-sm text-gray-400">Drop an image here or click to upload</span>
        <span className="text-xs text-gray-600 mt-1">JPEG, PNG, WebP, GIF &middot; Max 10MB</span>
      </label>
    </div>
  );
}
```

```tsx
// frontend/components/ContentInput/VideoUpload.tsx
"use client";

import { useCallback, useState } from "react";
import { Video, X } from "lucide-react";

interface Props {
  file: File | null;
  onChange: (file: File | null) => void;
}

export default function VideoUpload({ file, onChange }: Props) {
  const [preview, setPreview] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFile = useCallback(
    (f: File) => {
      if (f.size > 50 * 1024 * 1024) {
        alert("Video must be under 50MB");
        return;
      }
      if (!f.type.startsWith("video/")) {
        alert("Please upload a video file (MP4, MOV, WebM)");
        return;
      }
      onChange(f);
      setPreview(URL.createObjectURL(f));
    },
    [onChange]
  );

  const clear = () => {
    onChange(null);
    if (preview) URL.revokeObjectURL(preview);
    setPreview(null);
  };

  if (preview && file) {
    return (
      <div className="relative rounded-xl overflow-hidden border border-white/10">
        <video src={preview} className="w-full max-h-64 bg-black/50" controls />
        <button
          onClick={clear}
          className="absolute top-2 right-2 p-1.5 bg-black/60 rounded-full hover:bg-black/80 transition"
        >
          <X size={16} className="text-white" />
        </button>
        <div className="p-3 bg-white/5 text-xs text-gray-400">
          {file.name} &middot; {(file.size / 1024 / 1024).toFixed(1)}MB
        </div>
      </div>
    );
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        const f = e.dataTransfer.files[0];
        if (f) handleFile(f);
      }}
      className={`flex flex-col items-center justify-center h-48 border-2 border-dashed rounded-xl transition-all cursor-pointer
        ${dragOver ? "border-indigo-500 bg-indigo-500/10" : "border-white/10 hover:border-white/20 bg-white/5"}`}
    >
      <input
        type="file"
        accept="video/mp4,video/quicktime,video/webm"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (f) handleFile(f);
        }}
        className="hidden"
        id="video-upload"
      />
      <label htmlFor="video-upload" className="flex flex-col items-center cursor-pointer">
        <Video size={32} className="text-gray-500 mb-2" />
        <span className="text-sm text-gray-400">Drop a video here or click to upload</span>
        <span className="text-xs text-gray-600 mt-1">MP4, MOV, WebM &middot; Max 50MB, 60s</span>
      </label>
    </div>
  );
}
```

```tsx
// frontend/components/ContentInput/index.tsx
"use client";

import { useState } from "react";
import { FileText, Image as ImageIcon, Video } from "lucide-react";
import type { ContentType } from "@/lib/types";
import TextInput from "./TextInput";
import ImageUpload from "./ImageUpload";
import VideoUpload from "./VideoUpload";

const TABS: { type: ContentType; label: string; Icon: typeof FileText }[] = [
  { type: "text", label: "Text", Icon: FileText },
  { type: "image", label: "Image", Icon: ImageIcon },
  { type: "video", label: "Video", Icon: Video },
];

interface Props {
  contentType: ContentType;
  onContentTypeChange: (type: ContentType) => void;
  text: string;
  onTextChange: (text: string) => void;
  imageFile: File | null;
  onImageChange: (file: File | null) => void;
  videoFile: File | null;
  onVideoChange: (file: File | null) => void;
}

export default function ContentInput({
  contentType,
  onContentTypeChange,
  text,
  onTextChange,
  imageFile,
  onImageChange,
  videoFile,
  onVideoChange,
}: Props) {
  return (
    <div className="space-y-4">
      <div className="flex gap-1 p-1 bg-white/5 rounded-lg w-fit">
        {TABS.map(({ type, label, Icon }) => (
          <button
            key={type}
            onClick={() => onContentTypeChange(type)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all
              ${
                contentType === type
                  ? "bg-white/10 text-white"
                  : "text-gray-500 hover:text-gray-300"
              }`}
          >
            <Icon size={16} />
            {label}
          </button>
        ))}
      </div>

      {contentType === "text" && <TextInput value={text} onChange={onTextChange} />}
      {contentType === "image" && <ImageUpload file={imageFile} onChange={onImageChange} />}
      {contentType === "video" && <VideoUpload file={videoFile} onChange={onVideoChange} />}
    </div>
  );
}
```

- [ ] **Step 7: Verify frontend builds**

```bash
cd frontend
npm run build
```

Expected: Build succeeds.

- [ ] **Step 8: Commit**

```bash
git add frontend/
git commit -m "feat: frontend scaffolding with content input tabs, platform selector, API client"
```

---

### Task 8: Frontend results components (ViralScore, DimensionChart, Suggestions, ImageInsights, KeyframeTimeline, RecommendationsBar)

**Files:**
- Create: `frontend/components/ViralScore.tsx`, `frontend/components/DimensionChart.tsx`, `frontend/components/Suggestions.tsx`, `frontend/components/ImageInsights.tsx`, `frontend/components/KeyframeTimeline.tsx`, `frontend/components/RecommendationsBar.tsx`

**Interfaces:**
- Consumes: `AnalyseResponse`, `DimensionScores`, `Suggestion`, `CvFeatures`, `VideoFeatures` from `@/lib/types`
- Produces: React components that render analysis results with animations

- [ ] **Step 1: Create ViralScore gauge**

```tsx
// frontend/components/ViralScore.tsx
"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import type { Confidence } from "@/lib/types";

interface Props {
  score: number;
  verdict: string;
  confidence: Confidence;
}

function getColor(score: number): string {
  if (score >= 80) return "#22c55e";
  if (score >= 60) return "#6366f1";
  if (score >= 40) return "#f59e0b";
  return "#ef4444";
}

export default function ViralScore({ score, verdict, confidence }: Props) {
  const [displayScore, setDisplayScore] = useState(0);
  const radius = 80;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (displayScore / 100) * circumference;
  const color = getColor(score);

  useEffect(() => {
    let frame = 0;
    const totalFrames = 60;
    const interval = setInterval(() => {
      frame++;
      setDisplayScore(Math.round((frame / totalFrames) * score));
      if (frame >= totalFrames) clearInterval(interval);
    }, 16);
    return () => clearInterval(interval);
  }, [score]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className="flex flex-col items-center"
    >
      <div className="relative w-48 h-48">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 200 200">
          <circle cx="100" cy="100" r={radius} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="12" />
          <motion.circle
            cx="100"
            cy="100"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.5, ease: "easeOut" }}
            style={{ filter: `drop-shadow(0 0 8px ${color}40)` }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-5xl font-bold text-white">{displayScore}</span>
          <span className="text-xs text-gray-400 mt-1">/ 100</span>
        </div>
      </div>
      <p className="mt-3 text-lg font-medium text-white">{verdict}</p>
      <span className="text-xs text-gray-500 mt-1 px-2 py-0.5 rounded-full bg-white/5">
        {confidence} confidence
      </span>
    </motion.div>
  );
}
```

- [ ] **Step 2: Create DimensionChart**

```tsx
// frontend/components/DimensionChart.tsx
"use client";

import { motion } from "framer-motion";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import type { DimensionScores } from "@/lib/types";

interface Props {
  scores: DimensionScores;
}

const DIMENSION_LABELS: Record<string, string> = {
  emotional_impact: "Emotion",
  social_currency: "Social currency",
  practical_value: "Practical value",
  narrative_strength: "Narrative",
  trigger_potential: "Triggers",
  shareability: "Shareability",
  platform_fit: "Platform fit",
  hook_quality: "Hook",
};

export default function DimensionChart({ scores }: Props) {
  const data = Object.entries(scores).map(([key, val]) => ({
    dimension: DIMENSION_LABELS[key] || key,
    score: val.score,
    detail: val.detail,
    fullMark: 100,
  }));

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6, delay: 0.3 }}
    >
      <ResponsiveContainer width="100%" height={320}>
        <RadarChart data={data} cx="50%" cy="50%" outerRadius="75%">
          <PolarGrid stroke="rgba(255,255,255,0.08)" />
          <PolarAngleAxis
            dataKey="dimension"
            tick={{ fill: "#9ca3af", fontSize: 11 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fill: "#6b7280", fontSize: 10 }}
            axisLine={false}
          />
          <Radar
            name="Score"
            dataKey="score"
            stroke="#6366f1"
            fill="#6366f1"
            fillOpacity={0.2}
            strokeWidth={2}
          />
          <Tooltip
            content={({ payload }) => {
              if (!payload?.length) return null;
              const d = payload[0].payload;
              return (
                <div className="bg-gray-900 border border-white/10 rounded-lg p-3 text-sm max-w-xs">
                  <p className="font-medium text-white">
                    {d.dimension}: {d.score}/100
                  </p>
                  <p className="text-gray-400 mt-1">{d.detail}</p>
                </div>
              );
            }}
          />
        </RadarChart>
      </ResponsiveContainer>

      <div className="grid grid-cols-2 gap-2 mt-4">
        {data.map((d) => (
          <div key={d.dimension} className="flex items-center justify-between px-3 py-1.5 rounded-lg bg-white/5">
            <span className="text-xs text-gray-400">{d.dimension}</span>
            <span
              className="text-sm font-medium"
              style={{ color: d.score >= 70 ? "#22c55e" : d.score >= 50 ? "#f59e0b" : "#ef4444" }}
            >
              {d.score}
            </span>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
```

- [ ] **Step 3: Create Suggestions component**

```tsx
// frontend/components/Suggestions.tsx
"use client";

import { motion } from "framer-motion";
import { CheckCircle, XCircle, Lightbulb } from "lucide-react";
import type { Suggestion } from "@/lib/types";

interface Props {
  strengths: string[];
  weaknesses: string[];
  suggestions: Suggestion[];
  rewrittenHook: string | null;
  thumbnailSuggestions: string | null;
}

const PRIORITY_STYLES = {
  high: "bg-red-500/10 text-red-400 border-red-500/20",
  medium: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  low: "bg-blue-500/10 text-blue-400 border-blue-500/20",
};

export default function Suggestions({
  strengths,
  weaknesses,
  suggestions,
  rewrittenHook,
  thumbnailSuggestions,
}: Props) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="p-4 rounded-xl border border-green-500/20 bg-green-500/5"
        >
          <h3 className="text-sm font-medium text-green-400 mb-3 flex items-center gap-2">
            <CheckCircle size={16} /> Strengths
          </h3>
          <ul className="space-y-2">
            {strengths.map((s, i) => (
              <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                <span className="text-green-500 mt-0.5">+</span> {s}
              </li>
            ))}
          </ul>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="p-4 rounded-xl border border-red-500/20 bg-red-500/5"
        >
          <h3 className="text-sm font-medium text-red-400 mb-3 flex items-center gap-2">
            <XCircle size={16} /> Weaknesses
          </h3>
          <ul className="space-y-2">
            {weaknesses.map((w, i) => (
              <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                <span className="text-red-500 mt-0.5">-</span> {w}
              </li>
            ))}
          </ul>
        </motion.div>
      </div>

      <div className="space-y-3">
        {suggestions.map((s, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 + i * 0.1 }}
            className={`p-4 rounded-xl border ${PRIORITY_STYLES[s.priority]}`}
          >
            <div className="flex items-start gap-3">
              <Lightbulb size={16} className="mt-0.5 shrink-0" />
              <div>
                <span className="text-xs font-medium uppercase tracking-wide opacity-60">{s.priority}</span>
                <p className="text-sm text-gray-200 mt-1">{s.text}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>

      {rewrittenHook && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.9 }}
          className="p-4 rounded-xl border border-indigo-500/20 bg-indigo-500/5"
        >
          <h3 className="text-sm font-medium text-indigo-400 mb-2">Rewritten hook</h3>
          <p className="text-sm text-gray-200 italic">&ldquo;{rewrittenHook}&rdquo;</p>
        </motion.div>
      )}

      {thumbnailSuggestions && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.9 }}
          className="p-4 rounded-xl border border-purple-500/20 bg-purple-500/5"
        >
          <h3 className="text-sm font-medium text-purple-400 mb-2">Visual suggestions</h3>
          <p className="text-sm text-gray-200">{thumbnailSuggestions}</p>
        </motion.div>
      )}
    </div>
  );
}
```

- [ ] **Step 4: Create RecommendationsBar**

```tsx
// frontend/components/RecommendationsBar.tsx
"use client";

import { motion } from "framer-motion";
import { Clock, Hash, Info } from "lucide-react";

interface Props {
  bestPostingTimes: string[];
  recommendedHashtags: string[];
  emotionsDetected: string[];
}

export default function RecommendationsBar({
  bestPostingTimes,
  recommendedHashtags,
  emotionsDetected,
}: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1 }}
      className="grid grid-cols-1 md:grid-cols-3 gap-4"
    >
      <div className="p-4 rounded-xl bg-white/5 border border-white/10">
        <h3 className="text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
          <Clock size={14} /> Best posting times
        </h3>
        <div className="space-y-1">
          {bestPostingTimes.map((t, i) => (
            <p key={i} className="text-sm text-gray-400">{t}</p>
          ))}
        </div>
      </div>

      <div className="p-4 rounded-xl bg-white/5 border border-white/10">
        <h3 className="text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
          <Hash size={14} /> Recommended hashtags
        </h3>
        <div className="flex flex-wrap gap-1.5">
          {recommendedHashtags.map((tag, i) => (
            <span key={i} className="text-xs px-2 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              {tag}
            </span>
          ))}
        </div>
      </div>

      <div className="p-4 rounded-xl bg-white/5 border border-white/10">
        <h3 className="text-sm font-medium text-gray-300 mb-2 flex items-center gap-2">
          <Info size={14} /> Emotions detected
        </h3>
        <div className="flex flex-wrap gap-1.5">
          {emotionsDetected.map((e, i) => (
            <span key={i} className="text-xs px-2 py-1 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
              {e}
            </span>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
```

- [ ] **Step 5: Create ImageInsights and KeyframeTimeline stubs**

```tsx
// frontend/components/ImageInsights.tsx
"use client";

import { motion } from "framer-motion";
import type { CvFeatures } from "@/lib/types";

interface Props {
  features: CvFeatures;
}

export default function ImageInsights({ features }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5 }}
      className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-3"
    >
      <h3 className="text-sm font-medium text-gray-300">Image analysis</h3>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="text-center">
          <p className="text-2xl font-bold text-white">{features.width}x{features.height}</p>
          <p className="text-xs text-gray-500">Dimensions</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-white">{features.face_count}</p>
          <p className="text-xs text-gray-500">Faces detected</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-white">{Math.round(features.brightness_score)}</p>
          <p className="text-xs text-gray-500">Brightness</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-white">{Math.round(features.composition_score)}</p>
          <p className="text-xs text-gray-500">Composition</p>
        </div>
      </div>
      {features.dominant_colors.length > 0 && (
        <div>
          <p className="text-xs text-gray-500 mb-2">Dominant colors</p>
          <div className="flex gap-2">
            {features.dominant_colors.slice(0, 5).map((c, i) => (
              <div
                key={i}
                className="w-8 h-8 rounded-lg border border-white/10"
                style={{ backgroundColor: `rgb(${c[0]}, ${c[1]}, ${c[2]})` }}
              />
            ))}
          </div>
        </div>
      )}
      {features.has_text_overlay && (
        <div className="text-xs text-gray-400">
          Text detected on image: &ldquo;{features.detected_text.slice(0, 100)}&rdquo;
        </div>
      )}
    </motion.div>
  );
}
```

```tsx
// frontend/components/KeyframeTimeline.tsx
"use client";

import { motion } from "framer-motion";
import type { VideoFeatures } from "@/lib/types";

interface Props {
  features: VideoFeatures;
}

export default function KeyframeTimeline({ features }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5 }}
      className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-3"
    >
      <h3 className="text-sm font-medium text-gray-300">Video analysis</h3>
      <div className="grid grid-cols-3 gap-3">
        <div className="text-center">
          <p className="text-2xl font-bold text-white">{features.duration_seconds.toFixed(1)}s</p>
          <p className="text-xs text-gray-500">Duration</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-white">{features.keyframe_count}</p>
          <p className="text-xs text-gray-500">Keyframes</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-white">{features.has_audio ? "Yes" : "No"}</p>
          <p className="text-xs text-gray-500">Audio</p>
        </div>
      </div>
      {features.transcript && (
        <div>
          <p className="text-xs text-gray-500 mb-1">Transcript</p>
          <p className="text-sm text-gray-300 bg-black/30 rounded-lg p-3 max-h-32 overflow-y-auto">
            {features.transcript}
          </p>
        </div>
      )}
    </motion.div>
  );
}
```

- [ ] **Step 6: Verify build**

```bash
cd frontend
npm run build
```

Expected: Build succeeds.

- [ ] **Step 7: Commit**

```bash
git add frontend/components/
git commit -m "feat: results components — ViralScore gauge, radar chart, suggestions, image/video insights"
```

---

### Task 9: Analysis page (assemble everything) + end-to-end integration

**Files:**
- Modify: `frontend/app/layout.tsx`, `frontend/app/page.tsx`, `frontend/app/globals.css`, `frontend/app/analyse/page.tsx`

**Interfaces:**
- Consumes: All components from Tasks 7-8, `analyseContent` from `@/lib/api`
- Produces: Working single-page app at `/analyse` with full analysis flow

- [ ] **Step 1: Update globals.css**

```css
/* frontend/app/globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --background: #09090b;
  --foreground: #fafafa;
}

body {
  background: var(--background);
  color: var(--foreground);
  font-family: system-ui, -apple-system, sans-serif;
}

/* Subtle grid background */
body::before {
  content: "";
  position: fixed;
  inset: 0;
  background-image: radial-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 32px 32px;
  pointer-events: none;
  z-index: -1;
}
```

- [ ] **Step 2: Update layout.tsx**

```tsx
// frontend/app/layout.tsx
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Viralify — Predict your content's viral potential",
  description: "AI-powered content analysis for text, images, and video. Get a viral score with actionable suggestions.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
```

- [ ] **Step 3: Create redirect page**

```tsx
// frontend/app/page.tsx
import { redirect } from "next/navigation";

export default function Home() {
  redirect("/analyse");
}
```

- [ ] **Step 4: Build the analysis page**

```tsx
// frontend/app/analyse/page.tsx
"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, Loader2 } from "lucide-react";

import ContentInput from "@/components/ContentInput";
import PlatformSelector from "@/components/PlatformSelector";
import ViralScore from "@/components/ViralScore";
import DimensionChart from "@/components/DimensionChart";
import Suggestions from "@/components/Suggestions";
import ImageInsights from "@/components/ImageInsights";
import KeyframeTimeline from "@/components/KeyframeTimeline";
import RecommendationsBar from "@/components/RecommendationsBar";

import { analyseContent } from "@/lib/api";
import type { AnalyseResponse, ContentType, Platform } from "@/lib/types";

const LOADING_MESSAGES: Record<ContentType, string[]> = {
  text: ["Analysing text patterns...", "Running STEPPS framework...", "Generating suggestions..."],
  image: ["Extracting visual features...", "Analysing composition...", "Evaluating viral potential..."],
  video: ["Extracting keyframes...", "Transcribing audio...", "Analysing content..."],
};

export default function AnalysePage() {
  const [contentType, setContentType] = useState<ContentType>("text");
  const [platform, setPlatform] = useState<Platform>("twitter");
  const [text, setText] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [result, setResult] = useState<AnalyseResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canAnalyse =
    (contentType === "text" && text.trim().length >= 10) ||
    (contentType === "image" && imageFile !== null) ||
    (contentType === "video" && videoFile !== null);

  async function handleAnalyse() {
    setLoading(true);
    setError(null);
    setResult(null);

    const messages = LOADING_MESSAGES[contentType];
    let msgIdx = 0;
    setLoadingMessage(messages[0]);
    const interval = setInterval(() => {
      msgIdx = (msgIdx + 1) % messages.length;
      setLoadingMessage(messages[msgIdx]);
    }, 2000);

    try {
      const response = await analyseContent({
        contentType,
        platform,
        content: contentType === "text" ? text : undefined,
        file: contentType === "image" ? imageFile! : contentType === "video" ? videoFile! : undefined,
      });
      setResult(response);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed. Please try again.");
    } finally {
      setLoading(false);
      clearInterval(interval);
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-white tracking-tight">
          Viral<span className="text-indigo-500">ify</span>
        </h1>
        <p className="text-gray-400 mt-2">Predict your content&apos;s viral potential with AI</p>
      </div>

      {/* Input section */}
      <div className="space-y-6 mb-8">
        <ContentInput
          contentType={contentType}
          onContentTypeChange={(t) => {
            setContentType(t);
            setResult(null);
            setError(null);
          }}
          text={text}
          onTextChange={setText}
          imageFile={imageFile}
          onImageChange={setImageFile}
          videoFile={videoFile}
          onVideoChange={setVideoFile}
        />

        <PlatformSelector selected={platform} onChange={setPlatform} />

        <button
          onClick={handleAnalyse}
          disabled={!canAnalyse || loading}
          className="w-full py-3 px-6 rounded-xl font-medium text-white transition-all
            bg-indigo-600 hover:bg-indigo-500 disabled:opacity-40 disabled:cursor-not-allowed
            shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40
            flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <Loader2 size={18} className="animate-spin" />
              {loadingMessage}
            </>
          ) : (
            <>
              <Zap size={18} />
              Analyse viral potential
            </>
          )}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm mb-8">
          {error}
        </div>
      )}

      {/* Results */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="space-y-8"
          >
            {/* Score + Chart */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
              <ViralScore
                score={result.overall_score}
                verdict={result.verdict}
                confidence={result.confidence}
              />
              <DimensionChart scores={result.dimension_scores} />
            </div>

            {/* Content-specific insights */}
            {result.cv_features && result.content_type === "image" && (
              <ImageInsights features={result.cv_features} />
            )}
            {result.video_features && result.content_type === "video" && (
              <KeyframeTimeline features={result.video_features} />
            )}

            {/* Suggestions */}
            <Suggestions
              strengths={result.strengths}
              weaknesses={result.weaknesses}
              suggestions={result.suggestions}
              rewrittenHook={result.rewritten_hook}
              thumbnailSuggestions={result.thumbnail_suggestions}
            />

            {/* Recommendations */}
            <RecommendationsBar
              bestPostingTimes={result.best_posting_times}
              recommendedHashtags={result.recommended_hashtags}
              emotionsDetected={result.emotions_detected}
            />

            {/* Processing time */}
            <p className="text-xs text-gray-600 text-center">
              Analysed in {(result.processing_time_ms / 1000).toFixed(1)}s
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
```

- [ ] **Step 5: Verify full build**

```bash
cd frontend
npm run build
```

Expected: Build succeeds with no errors.

- [ ] **Step 6: Commit**

```bash
git add frontend/app/
git commit -m "feat: analysis page with full input-to-results flow"
```

---

### Task 10: Docker Compose, deployment config, and end-to-end verification

**Files:**
- Create: `docker-compose.yml`
- Verify: full end-to-end flow locally

**Interfaces:**
- Consumes: Backend (FastAPI on port 8000), Frontend (Next.js on port 3000)
- Produces: Working local dev environment via `docker compose up`

- [ ] **Step 1: Create docker-compose.yml**

```yaml
# docker-compose.yml
version: "3.8"

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file: ./backend/.env
    environment:
      - CORS_ORIGINS=http://localhost:3000
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    env_file: ./frontend/.env.local
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    command: npm run dev
    depends_on:
      - backend
```

- [ ] **Step 2: Create frontend Dockerfile**

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]
```

- [ ] **Step 3: Run full test suite**

```bash
cd backend
pytest tests/ -v --tb=short
```

Expected: All tests pass.

```bash
cd frontend
npm run build
```

Expected: Build succeeds.

- [ ] **Step 4: Manual end-to-end verification**

```bash
# Terminal 1
cd backend
cp .env.example .env  # fill in GEMINI_API_KEY and GROQ_API_KEY
uvicorn app.main:app --reload --port 8000

# Terminal 2
cd frontend
cp .env.local.example .env.local
npm run dev
```

Open http://localhost:3000. Verify:
1. Page loads with Viralify header
2. Text/Image/Video tabs switch correctly
3. Platform selector works
4. Submitting text analysis returns results
5. Score gauge animates
6. Radar chart displays
7. Suggestions render with priority colors

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml frontend/Dockerfile
git commit -m "feat: docker compose and deployment configuration"
```

---

### Task 11: UI polish pass (animations, responsive, design refinement)

**Files:**
- Modify: All frontend component files as needed for visual polish.

**Interfaces:**
- Consumes: All existing components
- Produces: Polished, responsive, animated UI. Use `frontend-design` and `impeccable` skills during implementation.

This task is intentionally open — invoke the `frontend-design` and `impeccable` skills during implementation to achieve the premium, one-of-a-kind aesthetic described in the spec. Focus areas:

- [ ] **Step 1: Custom color palette** — replace stock indigo with a signature gradient/palette. Add content-type accent colors (warm for text, cool for image, electric for video).

- [ ] **Step 2: Typography hierarchy** — add Inter or a premium font. Set up heading/body/mono scale in Tailwind config.

- [ ] **Step 3: Score reveal animation** — enhance the gauge with a particle/ripple effect on completion. Add counting animation with easing.

- [ ] **Step 4: Responsive layout** — ensure the analysis page works well on mobile (stack score + chart, full-width cards).

- [ ] **Step 5: Loading states** — add a skeleton/shimmer state for the results area while loading. Progressive loading messages per content type.

- [ ] **Step 6: Dark/light mode** — wire up Tailwind dark mode toggle if time permits, or default to dark-only (matching spec's "theater mode" for results).

- [ ] **Step 7: Final visual review** — screenshot the app, compare to Linear/Raycast/Vercel quality bar. Fix any rough edges.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "polish: premium UI with custom palette, animations, responsive design"
```
