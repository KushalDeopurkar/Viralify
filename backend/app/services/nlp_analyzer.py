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
    r"little known|most people don't|everything you know|"
    r"change everything|shocking revelation)\b",
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
