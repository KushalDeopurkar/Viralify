# Viralify — Product Spec

## 1. What is Viralify

A tool that analyses content and predicts viral potential. Users paste text, pick a platform, get a score (0-100) with detailed breakdown and actionable suggestions.

Target users: content creators, social media managers, marketers.

## 2. The science behind it

Based on Jonah Berger's STEPPS framework (Wharton research, published in "Contagious: Why Things Catch On"):

| Principle | Signal | How we measure |
|---|---|---|
| Social Currency | Makes sharer look smart/cool | Novelty, insider knowledge, exclusivity language |
| Triggers | Environmental cues remind people | Current events alignment, daily routine hooks |
| Emotion | High-arousal emotions drive sharing | Sentiment polarity + arousal (awe, anger > sadness) |
| Public | Visible = imitable | Social proof signals, observable actions |
| Practical Value | Useful info gets shared | How-to detection, listicle format, actionable content |
| Stories | Narrative wrappers carry messages | Story arc, character presence, conflict/resolution |

Key research finding: content triggering high-arousal emotions is 34% more likely to go viral.

Realistic accuracy: 60-70% for pre-publication prediction. With early engagement signals, 80%+. Frame as "viral potential", not guarantee.

## 3. Analysis dimensions (8 scores, each 0-100)

1. **Emotional impact** — what emotions, how intense, high-arousal or low-arousal
2. **Social currency** — does sharing make the sharer look informed/cool
3. **Practical value** — actionable? tips/how-to/framework?
4. **Narrative strength** — story arc, character, conflict present?
5. **Trigger potential** — connected to daily routines, current events, seasons?
6. **Shareability** — would someone tag a friend? screenshot-worthy? hot take?
7. **Platform fit** — format matches platform norms? right length/media/hashtags?
8. **Hook quality** — first line grabs attention? curiosity gap?

## 4. NLP features extracted locally

### Readability
- Flesch Reading Ease (0-100 scale, higher = easier)
- Flesch-Kincaid Grade Level (US grade level)
- Gunning Fog index
- SMOG index
- Reading time (seconds, based on 250 WPM)
- Mass appeal score (peaks at grade 6-8)

### Sentiment
- VADER compound score (-1 to 1)
- Positive/negative/neutral ratios
- Arousal level (high/medium/low based on |compound|)
- Arousal score (0-100)
- Dominant tone (positive/negative/neutral)
- Emotion category detection (high-arousal positive, high-arousal negative, low-arousal positive, low-arousal negative)

### Structure
- Word count, char count, sentence count, paragraph count
- Average sentence length, average word length
- Question detection + count
- List format detection
- Emoji detection + count
- Hashtag extraction + count
- Mention count, URL count
- CAPS emphasis detection
- First line extraction + length

### Engagement signals
- Power word count + which ones found (30-word lexicon: "secret", "shocking", "hack", etc.)
- Call-to-action detection ("share", "tag", "follow", "subscribe", etc.)
- Number/statistic presence
- Controversy markers ("unpopular opinion", "hot take", "change my mind")
- Personal story markers ("I learned", "my experience", "true story")
- Curiosity gap markers ("you won't believe", "here's why", "turns out")
- Social proof markers ("went viral", "trending", "everyone")
- Urgency markers ("now", "limited", "breaking", "just happened")

### Platform fit
- Platform-specific optimal ranges:
  - Twitter: 71-280 chars, 1-2 hashtags
  - LinkedIn: 1300-2000 chars, 3-5 hashtags
  - Instagram: 138-150 chars, 5-10 hashtags
  - Reddit: 100-800 chars, 0 hashtags
  - TikTok: 80-150 chars, 3-5 hashtags
  - YouTube: 200-500 chars, 2-4 hashtags
  - Blog: 1500-2500 words, 0 hashtags
- Length fit score (0-100)
- Hashtag fit score (0-100)
- Overall platform score (average of length + hashtag fit)

## 5. Claude API prompt

The prompt sends:
- Raw content (capped at 5000 chars)
- Platform name
- Pre-computed NLP features as JSON
- Optional author context (followers, engagement rate)

Asks Claude to return JSON-only (no markdown, no backticks) with:
- overall_score (0-100)
- verdict (5 tiers from "Will likely go viral" to "Below average reach")
- dimension_scores (8 dimensions, each with score + 1-sentence detail)
- emotions_detected (top 2-3)
- strengths (3 items)
- weaknesses (2 items)
- suggestions (3 items, each with priority high/medium/low)
- rewritten_hook (improved opening line)
- best_posting_times (2 suggestions)
- recommended_hashtags (5 tags)
- confidence (high/medium/low)

Calibration guidance in prompt: 50 = average, 70+ = strong, 85+ = exceptional. Most content should land 40-65.

## 6. UI components

### ViralScore gauge
- Circular SVG ring, animated fill with Framer Motion
- Color-coded: green (80+), blue (60-79), amber (40-59), red (<40)
- Large number in center, verdict below, confidence label

### DimensionChart
- Recharts RadarChart with 8 axes
- Indigo fill, interactive tooltip showing detail text
- Score grid below chart: 2-column, color-coded numbers

### Suggestions
- Strengths card (green border, checkmarks)
- Weaknesses card (red border, X marks)
- 3 suggestion cards with priority badges (high=red, medium=amber, low=blue)
- Rewritten hook card (indigo, italic quote)

### AnalysePage (main page)
- Platform selector (pill buttons, 8 options)
- Textarea with char/word counter
- Analyse button (indigo, loading spinner)
- Results: score + chart side-by-side, stat cards, suggestions, hashtags, timing
- AnimatePresence for smooth transitions

## 7. Database tables

```sql
-- profiles: extends Supabase auth
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    name TEXT,
    plan TEXT DEFAULT 'free',
    analyses_today INT DEFAULT 0,
    analyses_reset_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- analyses: every analysis run
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id),
    content_text TEXT NOT NULL,
    platform TEXT NOT NULL DEFAULT 'general',
    overall_score INT,
    dimension_scores JSONB DEFAULT '{}',
    nlp_features JSONB DEFAULT '{}',
    suggestions JSONB DEFAULT '[]',
    claude_response JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- feedback: user reports actual performance (for future ML)
CREATE TABLE feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES analyses(id),
    actually_went_viral BOOLEAN DEFAULT FALSE,
    actual_engagement JSONB DEFAULT '{}',
    reported_at TIMESTAMPTZ DEFAULT NOW()
);
```

RLS enabled. Indexes on user_id, created_at, score, analysis_id.

## 8. Scoring calibration

The overall_score is a weighted average Claude computes from 8 dimensions. Guide Claude to be calibrated:

| Score range | Verdict | Meaning |
|---|---|---|
| 85-100 | Will likely go viral | Exceptional on multiple dimensions, strong hook + emotion + platform fit |
| 70-84 | Has strong viral potential | Strong on most dimensions, minor gaps |
| 55-69 | Good reach potential | Solid content, needs optimization on 2-3 dimensions |
| 40-54 | Average reach | Typical content, several areas to improve |
| 0-39 | Below average reach | Significant issues across multiple dimensions |

## 9. Error handling

- Claude API timeout/failure: return HTTP 502 with error message
- Content too short (<10 chars): return HTTP 422 validation error
- Content too long (>10000 chars): truncate at 5000 for Claude, full for NLP
- JSON parse failure from Claude: retry once, then return error with raw response snippet
- DB save failure: swallow silently, never block the analysis response
- Rate limit hit: return HTTP 429 with remaining time

## 10. Performance targets

- NLP pipeline: <100ms
- Claude analysis: <5s (p95)
- Full round-trip: <6s
- Quick analysis (NLP-only): <200ms
