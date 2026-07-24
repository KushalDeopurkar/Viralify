# Viralify

AI-powered content analysis that predicts viral potential using NLP and the STEPPS framework.

## Architecture

```
Frontend (Next.js)  →  Backend (FastAPI)  →  Claude API (Analysis)
                            ↓                      ↓
                    NLP Pipeline (local)    STEPPS Framework
                            ↓
                    Supabase (PostgreSQL)
```

## Quick start

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Download NLTK data
python -c "import nltk; nltk.download('vader_lexicon')"

# Configure
cp .env.example .env
# Edit .env with your Anthropic API key + Supabase credentials

# Run
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install

# Configure
cp .env.local.example .env.local
# Edit with your API URL

# Run
npm run dev
```

### 3. Database

1. Create a Supabase project at https://supabase.com
2. Run `backend/supabase_migration.sql` in the SQL Editor
3. Copy your project URL + keys into `.env` files

### Docker (alternative)

```bash
docker compose up
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/analyse` | Full analysis (NLP + Claude) |
| POST | `/api/analyse/quick` | NLP-only instant analysis |
| GET | `/api/health` | Health check |

## How it works

1. User pastes content and selects target platform
2. Backend runs local NLP pipeline (~50ms): readability, sentiment, structure, engagement signals
3. NLP features + content sent to Claude API for deep STEPPS analysis (~3-5s)
4. Claude returns dimension scores, suggestions, rewritten hook
5. Frontend renders animated dashboard with scores, radar chart, suggestions

## Tech stack

- **Frontend:** Next.js 14, Tailwind CSS, Recharts, Framer Motion
- **Backend:** FastAPI, textstat, VADER, NLTK
- **AI:** Anthropic Claude API (claude-sonnet-4-6)
- **Database:** Supabase (PostgreSQL)
