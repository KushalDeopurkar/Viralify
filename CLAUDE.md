# CLAUDE.md — Viralify

## Project overview

Viralify is an AI-powered content analysis tool that predicts viral potential. Users paste content (tweets, LinkedIn posts, blog intros, video scripts, headlines), select a target platform, and get a detailed viral score with actionable suggestions.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│   Frontend   │────▶│  Backend API  │────▶│  Claude API   │
│  (Next.js)   │◀────│  (FastAPI)    │◀────│  (STEPPS)     │
└─────────────┘     └──────┬───────┘     └───────────────┘
                           │
                    ┌──────▼───────┐
                    │  NLP Pipeline │
                    │  (local, fast)│
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │  Supabase    │
                    │  (PostgreSQL)│
                    └──────────────┘
```

## Tech stack

- **Frontend:** Next.js 14+ (App Router), Tailwind CSS, Recharts, Framer Motion, Lucide icons
- **Backend:** Python 3.12+, FastAPI, Pydantic, uvicorn
- **NLP:** textstat, vaderSentiment, NLTK
- **AI:** Anthropic Claude API (claude-sonnet-4-6)
- **Database:** Supabase (PostgreSQL + Auth + RLS)
- **Infra:** Docker Compose for local dev, Vercel (frontend), Railway (backend)

## Project structure

```
viralify/
├── CLAUDE.md
├── README.md
├── docker-compose.yml
├── docs/
│   └── spec.md              # Full product spec (read this first)
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   ├── supabase_migration.sql
│   └── app/
│       ├── main.py           # FastAPI entrypoint
│       ├── config.py          # Settings from env vars
│       ├── models/
│       │   └── schemas.py     # Pydantic request/response models
│       ├── routers/
│       │   └── analyse.py     # /api/analyse endpoints
│       └── services/
│           ├── nlp_analyzer.py    # Local NLP feature extraction
│           ├── claude_analyzer.py # Claude API integration
│           └── database.py        # Supabase persistence
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── .env.local.example
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx           # Redirects to /analyse
│   │   ├── globals.css
│   │   └── analyse/
│   │       └── page.tsx       # Main analysis page
│   ├── components/
│   │   ├── ViralScore.tsx     # Animated circular gauge
│   │   ├── DimensionChart.tsx # Radar chart (8 dimensions)
│   │   └── Suggestions.tsx    # Priority-tagged suggestion cards
│   └── lib/
│       └── api.ts             # Typed API client
```

## How the analysis works

Two-phase analysis pipeline:

### Phase 1: Local NLP (~50ms, no API calls)
Extracts ~20 features instantly:
- **Readability:** Flesch-Kincaid grade, Gunning Fog, mass appeal score (sweet spot: grade 6-8)
- **Sentiment:** VADER compound score, arousal level (high/medium/low), dominant tone
- **Structure:** word count, sentence count, question detection, list detection, emoji, hashtags
- **Engagement signals:** power word count, call-to-action, controversy, curiosity gap, social proof, urgency
- **Platform fit:** length fit score, hashtag fit score vs platform optima

### Phase 2: Claude API (~3-5s)
Sends content + NLP features to Claude with structured prompt. Analyses against Berger's STEPPS framework:
1. **Emotional impact** (0-100) — arousal level, emotional arc
2. **Social currency** (0-100) — does sharing make the sharer look smart/cool
3. **Practical value** (0-100) — is content actionable, useful
4. **Narrative strength** (0-100) — story arc, character, conflict
5. **Trigger potential** (0-100) — connected to daily routines or current events
6. **Shareability** (0-100) — would someone tag a friend, screenshot-worthy
7. **Platform fit** (0-100) — format matches platform best practices
8. **Hook quality** (0-100) — first line grabs attention

Returns: overall score, verdict, dimension breakdown, emotions detected, strengths, weaknesses, 3 prioritised suggestions, rewritten hook, best posting times, recommended hashtags.

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/analyse` | Full analysis (NLP + Claude). Body: `{content, platform, author_followers?, author_avg_engagement?}` |
| POST | `/api/analyse/quick` | NLP-only instant scoring. Same body. Returns quick_score + nlp_features |
| GET | `/api/health` | Health check |

## Database schema

Three tables in Supabase:

**profiles** — extends auth.users: id (UUID, FK), name, plan (free/pro/team/enterprise), analyses_today, analyses_reset_at

**analyses** — id (UUID), user_id (FK nullable), content_text, platform, overall_score (0-100), dimension_scores (JSONB), nlp_features (JSONB), suggestions (JSONB), claude_response (JSONB), created_at

**feedback** — id (UUID), analysis_id (FK), actually_went_viral (bool), actual_engagement (JSONB: likes/shares/comments/views), reported_at

RLS enabled. Users see own data. Anonymous analyses allowed (user_id NULL).

## Supported platforms

twitter, linkedin, instagram, tiktok, reddit, youtube, blog, general

Each has optimal character/word ranges and hashtag counts coded in NLP analyzer.

## Claude prompt structure

The Claude prompt asks for JSON-only output with calibrated scoring:
- 50 = average content
- 70+ = strong
- 85+ = exceptional
- Most content should score 40-65

Prompt includes the raw content, pre-computed NLP features, and optional author context (follower count, engagement rate).

## Environment variables

### Backend (.env)
```
ANTHROPIC_API_KEY=sk-ant-xxxx
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

## Running locally

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -c "import nltk; nltk.download('vader_lexicon')"
cp .env.example .env  # fill in keys
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
cp .env.local.example .env.local  # fill in keys
npm run dev
```

Or: `docker compose up`

## Design direction

- Clean, modern, data-forward UI
- Indigo (#6366f1) as primary accent
- Dark mode support via Tailwind `dark:` classes
- Animated score reveal (Framer Motion)
- Radar chart for dimension breakdown (Recharts)
- Priority-coded suggestion cards (red=high, amber=medium, blue=low)
- Platform selector as pill buttons

## Key conventions

- Backend: snake_case everywhere, Pydantic models for all I/O, async endpoints
- Frontend: TypeScript strict, components in `components/`, page-level in `app/`
- All scores 0-100 integers
- Claude responses parsed as JSON, markdown fences stripped
- NLP pipeline is stateless — new instance per import, no side effects
- DB writes are fire-and-forget — never block the response on a save failure

## MVP scope (what to build first)

1. Content input with platform selector
2. Full analysis endpoint (NLP + Claude)
3. Viral score gauge (animated)
4. Dimension radar chart
5. Strengths/weaknesses display
6. Suggestion cards with priority
7. Rewritten hook display
8. Hashtag + timing recommendations

## Future (don't build yet)

- Auth/login flow
- Analysis history page
- URL scraping (paste article URL)
- A/B test generator
- Chrome extension
- User feedback loop for ML training
- Trending topic alignment
