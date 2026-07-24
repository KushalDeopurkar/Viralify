# Viralify multimodal design spec

**Date:** 2026-07-24
**Status:** Draft
**Scope:** Full-stack web app for predicting content virality across text, images, and video

---

## 1. Problem statement

Content creators, marketers, and social media managers lack a tool that predicts whether their content will go viral *before* they post it. Existing solutions are either text-only, paid, or limited to a single platform. Viralify analyses text, images, and video against Jonah Berger's STEPPS framework and returns a viral score (0-100) with actionable suggestions.

## 2. Constraints

- **Budget:** Zero. This is a final-year college project.
- **Timeline:** ~1 month.
- **AI provider:** Google Gemini free tier (1,500 req/day, 10 RPM, full vision support). Groq free tier for Whisper transcription (2,000 req/day).
- **Hosting:** Vercel free tier (frontend), Render free tier (backend, 512MB RAM, cold starts), Supabase free tier (database, 500MB).
- **No auth** for MVP. Anonymous analyses only.

## 3. Architecture

```
                         ┌──────────────────┐
                         │    Frontend       │
                         │  Next.js (Vercel) │
                         └────────┬─────────┘
                                  │ multipart/form-data
                         ┌────────▼─────────┐
                         │    Backend API    │
                         │  FastAPI (Render) │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
     ┌────────▼───────┐ ┌────────▼───────┐ ┌────────▼───────┐
     │  Text pipeline │ │ Image pipeline │ │ Video pipeline │
     │  NLP (local)   │ │ CV (local)     │ │ FFmpeg+Whisper │
     └────────┬───────┘ └────────┬───────┘ └────────┬───────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │ content + features
                         ┌────────▼─────────┐
                         │  Gemini API      │
                         │  STEPPS scoring  │
                         └────────┬─────────┘
                                  │
                         ┌────────▼─────────┐
                         │  Supabase        │
                         │  (PostgreSQL)    │
                         └──────────────────┘
```

Two-phase pipeline:
- **Phase 1 (feature extraction):** Content-type-specific feature extraction. ~50-200ms for text/images (fully local, no API calls). For video: ~2-3s local FFmpeg extraction + ~3-5s Groq Whisper API call for transcription (runs in parallel).
- **Phase 2 (Gemini API, ~3-5s):** Content + extracted features sent to Gemini for STEPPS framework evaluation. Returns structured JSON.

## 4. Content types and processing pipelines

### 4.1 Text pipeline

User pastes text into a textarea. Local NLP extracts ~20 features instantly.

**Readability:** Flesch Reading Ease, Flesch-Kincaid Grade Level, Gunning Fog, SMOG, reading time, mass appeal score (peaks at grade 6-8).

**Sentiment:** VADER compound score, positive/negative/neutral ratios, arousal level (high/medium/low), dominant tone, emotion category.

**Structure:** Word count, char count, sentence count, paragraph count, avg sentence length, avg word length, question detection, list format, emoji count, hashtag count, mention count, URL count, CAPS detection, first line extraction.

**Engagement signals:** Power word count (30-word lexicon), CTA detection, number/statistic presence, controversy markers, personal story markers, curiosity gap markers, social proof markers, urgency markers.

**Platform fit:** Length fit score and hashtag fit score against platform-specific optimal ranges (Twitter 71-280 chars/1-2 hashtags, LinkedIn 1300-2000 chars/3-5 hashtags, etc.).

**Libraries:** textstat, vaderSentiment, NLTK.

### 4.2 Image pipeline

User uploads an image (max 10MB, JPEG/PNG/WebP/GIF). Local processing extracts visual features before sending to Gemini vision.

**Local features (Pillow + OpenCV):**
- Color dominance: top 5 colors via k-means clustering on downsampled pixels
- Brightness score (0-100): mean luminance of grayscale conversion
- Contrast score (0-100): standard deviation of luminance
- Image dimensions and aspect ratio
- Face count: OpenCV Haar cascade detector (frontal face)
- Text-on-image detection: pytesseract OCR (detects meme text, overlays, captions)
- Composition score: rule-of-thirds approximation (weighted interest in grid intersections)

**Gemini vision analysis:**
- Emotional resonance of the image
- Visual quality and aesthetic appeal
- Brand/trend alignment
- Shareability cues (meme potential, quote-ability)
- Platform fit (aspect ratio and style per platform)

**Libraries:** Pillow, OpenCV (opencv-python-headless), pytesseract, scikit-learn (for k-means).

### 4.3 Video pipeline

User uploads a short video (max 50MB, MP4/MOV/WebM, capped at 60 seconds). Most complex pipeline.

**Step 1 — Keyframe extraction (FFmpeg, local):**
Extract 5 evenly-spaced keyframes as JPEG. Select top 3 by visual variance (pixel histogram distance) for Gemini to keep token usage low.

**Step 2 — Audio extraction and transcription:**
FFmpeg extracts audio as WAV. Audio sent to Groq Whisper (free tier, 2,000 req/day) for transcription. If Whisper fails, fall back to keyframe-only analysis.

**Step 3 — Feature extraction:**
Each keyframe runs through the image pipeline's local features (color, brightness, faces, text overlay). The transcript runs through the text pipeline's NLP features (sentiment, readability, engagement signals).

**Step 4 — Gemini analysis:**
Top 3 keyframes + transcript + all extracted features sent to Gemini vision. Gemini evaluates the video holistically: emotional arc across frames, pacing, narrative flow, hook quality (first 3 seconds), audio-visual coherence.

**Libraries:** ffmpeg-python, Groq Python SDK.

**System dependencies (must be in Dockerfile):** FFmpeg (for keyframe/audio extraction), Tesseract OCR (for pytesseract text-on-image detection). Both are available via `apt-get install ffmpeg tesseract-ocr` in the backend Dockerfile.

## 5. STEPPS scoring framework

Eight dimensions, each scored 0-100. Signals evaluated depend on content type.

| Dimension | Text signals | Image signals | Video signals |
|---|---|---|---|
| Emotional impact | Sentiment, arousal words, emotional arc | Color mood, facial expressions, emotional tone | Emotional arc across frames, audio tone, facial expressions |
| Social currency | Insider knowledge, novelty, exclusivity | Aesthetic quality, trend alignment, uniqueness | Production value, uniqueness, "insider" feel |
| Practical value | How-to, lists, actionable tips | Infographic clarity, educational content | Tutorial structure, step clarity, takeaway value |
| Narrative strength | Story arc, character, conflict | Visual storytelling, implied narrative | Pacing, narrative flow, hook-to-payoff arc |
| Trigger potential | Current events, routine hooks, seasonal | Seasonal/cultural relevance, daily triggers | Trending audio, topical relevance, cultural moment |
| Shareability | Tag-a-friend, screenshot-worthy, hot take | Meme potential, quote-ability, reaction-worthy | Duet/stitch potential, reaction-worthy moments |
| Platform fit | Length, hashtags, format norms | Aspect ratio, resolution, visual style | Duration, format, caption overlay, vertical video |
| Hook quality | First line grabs attention, curiosity gap | Thumbnail appeal, visual hook | First 3 seconds engagement, opening frame |

**Calibration rules** (sent in Gemini prompt):
- 50 = average content
- 70+ = strong viral potential
- 85+ = exceptional (rare)
- Most content should score 40-65

**Verdicts:**
| Score | Verdict |
|---|---|
| 85-100 | Will likely go viral |
| 70-84 | Has strong viral potential |
| 55-69 | Good reach potential |
| 40-54 | Average reach |
| 0-39 | Below average reach |

## 6. Gemini prompt structure

System instruction defines the STEPPS framework, calibration rules, and output schema. User message includes:
- Raw content (text, or "see attached image/frames")
- Content type identifier
- Platform name
- Pre-computed local features as JSON
- Optional author context (followers, engagement rate)

Required JSON response:
```json
{
  "overall_score": 0-100,
  "verdict": "string (one of 5 tiers)",
  "dimension_scores": {
    "emotional_impact": {"score": 0-100, "detail": "one sentence"},
    "social_currency": {"score": 0-100, "detail": "..."},
    "practical_value": {"score": 0-100, "detail": "..."},
    "narrative_strength": {"score": 0-100, "detail": "..."},
    "trigger_potential": {"score": 0-100, "detail": "..."},
    "shareability": {"score": 0-100, "detail": "..."},
    "platform_fit": {"score": 0-100, "detail": "..."},
    "hook_quality": {"score": 0-100, "detail": "..."}
  },
  "emotions_detected": ["awe", "curiosity"],
  "strengths": ["str1", "str2", "str3"],
  "weaknesses": ["weak1", "weak2"],
  "suggestions": [
    {"text": "...", "priority": "high|medium|low"}
  ],
  "rewritten_hook": "improved opening line or null for images",
  "thumbnail_suggestions": "for images/video, null for text",
  "best_posting_times": ["Tuesday 9am EST", "Thursday 6pm EST"],
  "recommended_hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"],
  "confidence": "high|medium|low"
}
```

## 7. API endpoints

| Method | Path | Body | Description |
|---|---|---|---|
| POST | `/api/analyse` | `multipart/form-data`: `content_type` (text/image/video), `content` (text string, optional), `file` (uploaded file, optional), `platform`, `author_followers?`, `author_avg_engagement?` | Full two-phase analysis |
| POST | `/api/analyse/quick` | JSON: `{content, platform}` | Text-only NLP instant scoring |
| GET | `/api/health` | — | Health check + cold start warm-up |

Response format for `/api/analyse`:
```json
{
  "content_type": "text|image|video",
  "overall_score": 72,
  "verdict": "Has strong viral potential",
  "quick_score": 65,
  "nlp_features": {...},
  "cv_features": {...},
  "video_features": {...},
  "dimension_scores": {...},
  "emotions_detected": [...],
  "strengths": [...],
  "weaknesses": [...],
  "suggestions": [...],
  "rewritten_hook": "...",
  "thumbnail_suggestions": "...",
  "best_posting_times": [...],
  "recommended_hashtags": [...],
  "confidence": "medium",
  "processing_time_ms": 4200
}
```

## 8. Database schema

Three tables in Supabase (PostgreSQL). Extended from original spec.

```sql
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    name TEXT,
    plan TEXT DEFAULT 'free',
    analyses_today INT DEFAULT 0,
    analyses_reset_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE analyses (
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

CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analyses(id),
    actually_went_viral BOOLEAN DEFAULT FALSE,
    actual_engagement JSONB DEFAULT '{}',
    reported_at TIMESTAMPTZ DEFAULT NOW()
);
```

Indexes on `user_id`, `created_at`, `overall_score`, `content_type`, `analysis_id`.

RLS enabled. Anonymous analyses allowed (user_id NULL).

## 9. Frontend components

### Design direction

Premium, one-of-a-kind aesthetic. Not a generic template. Inspired by Linear, Raycast, Vercel dashboard quality. Will use `frontend-design` and `impeccable` skills during implementation.

Key principles:
- Generous whitespace, intentional typography hierarchy
- Smooth micro-interactions and signature animations
- Custom color palette (not stock Tailwind indigo)
- Content-type-specific accent colors
- Dark/light mode support
- "Theater mode" for results area (dark surface even in light mode)

### Components

**ContentInput/** — tabbed interface (Text / Image / Video). Text: textarea with live word/char counter. Image: drag-and-drop zone with instant preview. Video: drag-and-drop with duration display and 60s limit badge.

**PlatformSelector** — pill buttons for 8 platforms (Twitter, LinkedIn, Instagram, TikTok, Reddit, YouTube, Blog, General).

**ViralScore.tsx** — animated circular SVG gauge. Dramatic reveal: ring fills with animation, score counts up from 0, color transitions through the spectrum. Verdict text and confidence label below.

**DimensionChart.tsx** — Recharts RadarChart with 8 axes. Draws itself axis by axis with staggered animation. Interactive tooltip with detail text. Score grid below.

**Suggestions.tsx** — strengths card (green accents), weaknesses card (red accents), 3 suggestion cards with priority badges cascading in with staggered timing.

**KeyframeTimeline.tsx** (video-specific) — horizontal strip showing the 5 extracted keyframes. Highlights which frames contributed most to the score. Transcript excerpt below.

**ImageInsights.tsx** (image-specific) — annotated display showing composition grid overlay, color palette extraction, face detection markers.

**RecommendationsBar** — best posting times, recommended hashtags, platform-specific tips. Compact horizontal layout.

### Tech stack

Next.js 14+ (App Router), TypeScript strict, Tailwind CSS, Recharts, Framer Motion, Lucide icons.

### Page structure

```
/              → redirect to /analyse
/analyse       → main analysis page (input + results)
```

## 10. Supported platforms

twitter, linkedin, instagram, tiktok, reddit, youtube, blog, general

Each has optimal ranges for character/word count, hashtag count, aspect ratio (for images), and duration (for video) coded into the local analyzers.

## 11. Error handling

| Scenario | Behavior |
|---|---|
| Gemini API timeout/failure | Retry once, then fall back to NLP-only quick score with notice |
| Groq Whisper failure | Fall back to keyframe-only video analysis (skip transcript) |
| File too large | Client-side rejection (10MB images, 50MB video) before upload |
| Unsupported format | 422 with supported formats list |
| Video too long (>60s) | 422 rejection with clear message |
| Text too short (<10 chars) | 422 validation error |
| Text too long (>10,000 chars) | Truncate to 5,000 for Gemini, full for NLP |
| Gemini JSON parse failure | Retry once, then return error with raw response snippet |
| Render cold start (~30s) | Frontend shows "Waking up the servers..." loading state |
| DB save failure | Swallow silently, never block the analysis response |
| Gemini rate limit (10 RPM) | Server-side queue, show "Analysis queued" in frontend |
| Image with no visual content | Detect low-variance image, warn user |
| Video with no audio | Skip transcription, analyze visuals only |
| Very short video (<3s) | Extract all frames instead of sampling 5 |

## 12. Performance targets

| Pipeline | Target |
|---|---|
| Text NLP (local) | <100ms |
| Image CV (local) | <500ms |
| Video frame extraction (FFmpeg) | <3s |
| Whisper transcription (Groq) | <5s |
| Gemini analysis (text) | <5s |
| Gemini analysis (image) | <8s |
| Gemini analysis (video, 3 frames) | <12s |
| Full round-trip (text) | <6s |
| Full round-trip (image) | <10s |
| Full round-trip (video) | <20s |

## 13. Project structure

```
viralify/
├── CLAUDE.md
├── README.md
├── docker-compose.yml
├── docs/
│   ├── spec.md
│   └── superpowers/specs/
│       └── 2026-07-24-viralify-multimodal-design.md
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   ├── supabase_migration.sql
│   └── app/
│       ├── main.py                 # FastAPI entrypoint, CORS, lifespan
│       ├── config.py               # Settings from env vars
│       ├── models/
│       │   └── schemas.py          # Pydantic request/response models
│       ├── routers/
│       │   └── analyse.py          # /api/analyse endpoints
│       └── services/
│           ├── nlp_analyzer.py     # Text feature extraction (textstat, VADER, NLTK)
│           ├── image_analyzer.py   # Image feature extraction (Pillow, OpenCV, pytesseract)
│           ├── video_analyzer.py   # FFmpeg keyframes + pipeline orchestration
│           ├── gemini_analyzer.py  # Gemini API integration (text + vision)
│           ├── whisper_client.py   # Groq Whisper transcription client
│           └── database.py         # Supabase persistence
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── .env.local.example
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx                # Redirect to /analyse
│   │   ├── globals.css
│   │   └── analyse/
│   │       └── page.tsx            # Main analysis page
│   ├── components/
│   │   ├── ContentInput/
│   │   │   ├── TextInput.tsx
│   │   │   ├── ImageUpload.tsx
│   │   │   ├── VideoUpload.tsx
│   │   │   └── index.tsx           # Tabbed container
│   │   ├── PlatformSelector.tsx
│   │   ├── ViralScore.tsx          # Animated circular gauge
│   │   ├── DimensionChart.tsx      # Radar chart (8 dimensions)
│   │   ├── Suggestions.tsx         # Priority-tagged suggestion cards
│   │   ├── KeyframeTimeline.tsx    # Video keyframe strip
│   │   ├── ImageInsights.tsx       # Image analysis annotations
│   │   └── RecommendationsBar.tsx  # Hashtags, timing, tips
│   └── lib/
│       └── api.ts                  # Typed API client
│
└── tests/
    ├── test_nlp_analyzer.py
    ├── test_image_analyzer.py
    ├── test_video_analyzer.py
    └── test_gemini_analyzer.py
```

## 14. Environment variables

### Backend (.env)
```
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

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## 15. Testing strategy

- **Unit tests:** Each analyzer module (NLP, image, video) with sample inputs and expected feature ranges.
- **Integration tests:** Full pipeline with a sample text, image, and video. Mock Gemini/Groq responses.
- **Performance benchmarks:** Measure and document average latency per pipeline stage. Include in thesis.
- **Accuracy evaluation:** Manually score 20-30 pieces of real content, compare Viralify predictions to actual engagement. Document precision/recall in thesis.

## 16. Research references

Relevant datasets and papers for the thesis literature review:

- **Reddit-V dataset** (27K posts, multimodal): virality prediction benchmark with zero-shot LLM evaluation. CLIP and IDEFICS outperform zero-shot LLMs. Presented at RANLP 2025.
- **Understanding Image Virality** (Deza & Parikh, 2015): 10K Reddit images, identifies 5 visual attributes correlated with virality. Machines predict relative virality at 68% accuracy (humans: 60%).
- **Viraliency** (2017): Pooling local virality signals from image regions.
- **TikTok virality indicators** (ACM 2022): ML features for short video virality prediction. Random Forest outperforms linear regression.
- **STEPPS framework** (Berger, "Contagious: Why Things Catch On"): foundational theory. Content with high-arousal emotions is 34% more likely to go viral.
- **Early Multimodal Prediction of Cross-Lingual Meme Virality** (WebSci 2026): time-window analysis on Reddit memes.

## 17. MVP scope (build in this order)

1. Backend: Text NLP pipeline (port from existing spec)
2. Backend: Gemini integration (replace Claude API)
3. Backend: Image pipeline (Pillow + OpenCV + Gemini vision)
4. Backend: Video pipeline (FFmpeg + Groq Whisper + Gemini)
5. Frontend: Content input with tabs (Text/Image/Video) + platform selector
6. Frontend: Viral score gauge (animated)
7. Frontend: Dimension radar chart
8. Frontend: Suggestions, strengths/weaknesses
9. Frontend: Image-specific and video-specific result views
10. Frontend: Recommendations bar (hashtags, timing)
11. Integration: Connect frontend to backend, end-to-end flow
12. Database: Supabase setup, analysis persistence
13. Deployment: Vercel + Render + Supabase
14. Polish: Animations, micro-interactions, responsive, dark mode

## 18. Out of scope (do not build)

- User auth / login
- Analysis history page
- URL scraping
- A/B test generator
- Chrome extension
- Custom ML model training
- Paid plans / billing
