"""
Local NLP pipeline. Extracts ~20 features in <100ms, no API calls.
Used as input to Claude for richer analysis.
"""

import re
import textstat
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class NLPAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.power_words = {
            "secret", "shocking", "amazing", "incredible", "unbelievable",
            "breaking", "exclusive", "proven", "guaranteed", "free",
            "instant", "hack", "mistake", "truth", "exposed", "finally",
            "warning", "urgent", "limited", "revolutionary", "discover",
            "hidden", "insider", "banned", "controversial", "surprising",
            "mind-blowing", "game-changing", "ultimate", "essential",
        }
        self.emotion_words = {
            "high_arousal_positive": {
                "awesome", "thrilling", "exciting", "incredible", "mind-blowing",
                "ecstatic", "euphoric", "exhilarating", "stunning", "breathtaking",
                "awe-inspiring", "phenomenal", "spectacular",
            },
            "high_arousal_negative": {
                "outrageous", "furious", "disgusting", "horrifying", "shocking",
                "infuriating", "appalling", "enraging", "scandalous", "terrifying",
            },
            "low_arousal_positive": {
                "calm", "peaceful", "gentle", "relaxing", "soothing",
                "content", "pleasant", "comfortable",
            },
            "low_arousal_negative": {
                "sad", "depressing", "gloomy", "melancholy", "lonely",
                "hopeless", "disappointed", "tired",
            },
        }
        self.platform_optima = {
            "twitter": {"chars": (71, 280), "hashtags": (1, 2), "key": "chars"},
            "linkedin": {"chars": (1300, 2000), "hashtags": (3, 5), "key": "chars"},
            "instagram": {"chars": (138, 150), "hashtags": (5, 10), "key": "chars"},
            "reddit": {"chars": (100, 800), "hashtags": (0, 0), "key": "chars"},
            "tiktok": {"chars": (80, 150), "hashtags": (3, 5), "key": "chars"},
            "youtube": {"chars": (200, 500), "hashtags": (2, 4), "key": "chars"},
            "blog": {"words": (1500, 2500), "hashtags": (0, 0), "key": "words"},
        }

    def analyse(self, text: str, platform: str = "general") -> dict:
        return {
            "readability": self._readability(text),
            "sentiment": self._sentiment(text),
            "structure": self._structure(text),
            "engagement_signals": self._engagement_signals(text),
            "platform_fit": self._platform_fit(text, platform),
        }

    def _readability(self, text: str) -> dict:
        fk_grade = textstat.flesch_kincaid_grade(text)
        fre = textstat.flesch_reading_ease(text)
        return {
            "flesch_reading_ease": round(fre, 1),
            "flesch_kincaid_grade": round(fk_grade, 1),
            "gunning_fog": round(textstat.gunning_fog(text), 1),
            "smog_index": round(textstat.smog_index(text), 1),
            "reading_time_seconds": round(len(text.split()) / 4.2, 1),  # ~250 wpm
            # Grade 6-8 = mass appeal sweet spot
            "mass_appeal_score": max(0, min(100, round(100 - abs(fk_grade - 7) * 15))),
            "difficulty": (
                "very easy" if fre >= 80 else
                "easy" if fre >= 60 else
                "moderate" if fre >= 40 else
                "difficult" if fre >= 20 else
                "very difficult"
            ),
        }

    def _sentiment(self, text: str) -> dict:
        scores = self.vader.polarity_scores(text)
        compound = scores["compound"]
        arousal = abs(compound)

        # Detect emotion categories
        words_lower = set(text.lower().split())
        detected_emotions = []
        for category, word_set in self.emotion_words.items():
            matches = words_lower & word_set
            if matches:
                detected_emotions.append({
                    "category": category,
                    "words": list(matches),
                    "count": len(matches),
                })

        return {
            "compound": round(compound, 3),
            "positive": round(scores["pos"], 3),
            "negative": round(scores["neg"], 3),
            "neutral": round(scores["neu"], 3),
            "arousal_level": (
                "high" if arousal > 0.5 else
                "medium" if arousal > 0.2 else
                "low"
            ),
            "arousal_score": min(100, round(arousal * 130)),
            "dominant_tone": (
                "positive" if compound > 0.15 else
                "negative" if compound < -0.15 else
                "neutral"
            ),
            "emotion_categories": detected_emotions,
        }

    def _structure(self, text: str) -> dict:
        words = text.split()
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

        # First line analysis (hook)
        first_line = text.strip().split("\n")[0] if text.strip() else ""

        return {
            "word_count": len(words),
            "char_count": len(text),
            "sentence_count": len(sentences),
            "paragraph_count": len(paragraphs),
            "avg_sentence_length": round(len(words) / max(1, len(sentences)), 1),
            "avg_word_length": round(sum(len(w) for w in words) / max(1, len(words)), 1),
            "has_question": "?" in text,
            "question_count": text.count("?"),
            "has_exclamation": "!" in text,
            "has_list": bool(re.search(r"^\s*[\d\-\*\•]", text, re.MULTILINE)),
            "has_emoji": bool(re.search(r"[\U00010000-\U0010ffff\u2600-\u27BF\u2702-\u27B0]", text)),
            "emoji_count": len(re.findall(r"[\U00010000-\U0010ffff\u2600-\u27BF\u2702-\u27B0]", text)),
            "hashtag_count": len(re.findall(r"#\w+", text)),
            "hashtags": re.findall(r"#\w+", text),
            "mention_count": len(re.findall(r"@\w+", text)),
            "url_count": len(re.findall(r"https?://\S+", text)),
            "has_caps_emphasis": bool(re.search(r"\b[A-Z]{3,}\b", text)),
            "first_line": first_line[:200],
            "first_line_length": len(first_line.split()),
        }

    def _engagement_signals(self, text: str) -> dict:
        words_lower = set(text.lower().split())
        text_lower = text.lower()
        power_matches = words_lower & self.power_words

        return {
            "power_word_count": len(power_matches),
            "power_words_found": sorted(list(power_matches)),
            "has_call_to_action": bool(re.search(
                r"\b(share|retweet|tag|comment|follow|subscribe|click|try|check\s?out|dm|reply|save|bookmark|like)\b",
                text_lower
            )),
            "has_number_or_stat": bool(re.search(r"\d+%|\d+x|\$[\d,]+|\d{3,}", text)),
            "has_controversy": bool(re.search(
                r"\b(unpopular opinion|hot take|controversial|nobody talks about|truth is|"
                r"i disagree|fight me|change my mind|overrated|underrated)\b",
                text_lower
            )),
            "has_personal_story": bool(re.search(
                r"\b(i learned|my experience|happened to me|true story|i was|when i|"
                r"i realized|i discovered|let me tell you)\b",
                text_lower
            )),
            "has_curiosity_gap": bool(re.search(
                r"\b(you won.t believe|here.s why|the reason|what happened next|"
                r"turns out|the truth about|nobody expected|wait for it)\b",
                text_lower
            )),
            "has_social_proof": bool(re.search(
                r"\b(\d+[kKmM]?\s*(people|users|followers|views|likes)|"
                r"went viral|trending|everyone|most people)\b",
                text_lower
            )),
            "has_urgency": bool(re.search(
                r"\b(now|today|hurry|limited|last chance|don.t miss|before it.s gone|"
                r"breaking|just happened|right now)\b",
                text_lower
            )),
        }

    def _platform_fit(self, text: str, platform: str) -> dict:
        word_count = len(text.split())
        char_count = len(text)
        hashtag_count = len(re.findall(r"#\w+", text))

        result = {
            "platform": platform,
            "char_count": char_count,
            "word_count": word_count,
            "length_fit_score": 50,
            "hashtag_fit_score": 50,
            "overall_platform_score": 50,
            "length_advice": "",
            "hashtag_advice": "",
        }

        if platform not in self.platform_optima:
            result["length_advice"] = "Unknown platform — no specific guidance"
            return result

        opt = self.platform_optima[platform]

        # Length fit
        key = opt["key"]
        val = char_count if key == "chars" else word_count
        lo, hi = opt[key]
        if lo <= val <= hi:
            length_score = 100
            result["length_advice"] = f"Length is optimal for {platform}"
        elif val < lo:
            length_score = max(0, round(100 - (lo - val) / lo * 100))
            result["length_advice"] = f"Too short for {platform}. Aim for {lo}-{hi} {key}."
        else:
            length_score = max(0, round(100 - (val - hi) / hi * 100))
            result["length_advice"] = f"Too long for {platform}. Aim for {lo}-{hi} {key}."

        # Hashtag fit
        h_lo, h_hi = opt["hashtags"]
        if h_lo <= hashtag_count <= h_hi:
            hashtag_score = 100
            result["hashtag_advice"] = f"Hashtag count is optimal for {platform}"
        elif hashtag_count < h_lo:
            hashtag_score = max(0, round(hashtag_count / max(1, h_lo) * 100))
            result["hashtag_advice"] = f"Add more hashtags. Optimal for {platform}: {h_lo}-{h_hi}"
        else:
            hashtag_score = max(0, round(100 - (hashtag_count - h_hi) / max(1, h_hi) * 50))
            result["hashtag_advice"] = f"Too many hashtags. Optimal for {platform}: {h_lo}-{h_hi}"

        result["length_fit_score"] = round(length_score)
        result["hashtag_fit_score"] = round(hashtag_score)
        result["overall_platform_score"] = round((length_score + hashtag_score) / 2)

        return result
