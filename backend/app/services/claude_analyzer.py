"""
Claude API integration. Sends content + NLP features for deep STEPPS analysis.
Returns structured scores, suggestions, and rewritten hook.
"""

import json
import anthropic
from app.config import get_settings

ANALYSIS_PROMPT = """You are Viralify's analysis engine. Analyse this content for viral potential on {platform}.

CONTENT:
\"\"\"
{content}
\"\"\"

NLP FEATURES (pre-computed):
{nlp_features}

{author_context}

Analyse against Berger's STEPPS framework and platform best practices.
Score each dimension 0-100. Be calibrated: 50 = average content, 70+ = strong, 85+ = exceptional.
Most content should score 40-65. Only truly remarkable content hits 80+.

Return ONLY valid JSON (no markdown, no backticks, no preamble):
{{
  "overall_score": <0-100 weighted average>,
  "verdict": "<Will likely go viral | Has strong viral potential | Good reach potential | Average reach | Below average reach>",
  "dimension_scores": {{
    "emotional_impact": {{"score": <0-100>, "detail": "<1 sentence why>"}},
    "social_currency": {{"score": <0-100>, "detail": "<1 sentence why>"}},
    "practical_value": {{"score": <0-100>, "detail": "<1 sentence why>"}},
    "narrative_strength": {{"score": <0-100>, "detail": "<1 sentence why>"}},
    "trigger_potential": {{"score": <0-100>, "detail": "<1 sentence why>"}},
    "shareability": {{"score": <0-100>, "detail": "<1 sentence why>"}},
    "platform_fit": {{"score": <0-100>, "detail": "<1 sentence why>"}},
    "hook_quality": {{"score": <0-100>, "detail": "<1 sentence why>"}}
  }},
  "emotions_detected": ["<top 2-3 emotions>"],
  "strengths": ["<strength1>", "<strength2>", "<strength3>"],
  "weaknesses": ["<weakness1>", "<weakness2>"],
  "suggestions": [
    {{"priority": "high", "suggestion": "<specific actionable improvement>"}},
    {{"priority": "medium", "suggestion": "<specific actionable improvement>"}},
    {{"priority": "low", "suggestion": "<specific actionable improvement>"}}
  ],
  "rewritten_hook": "<improved opening line/headline that would score higher>",
  "best_posting_times": ["<day time1>", "<day time2>"],
  "recommended_hashtags": ["<tag1>", "<tag2>", "<tag3>", "<tag4>", "<tag5>"],
  "confidence": "<high|medium|low — based on how much signal the content provides>"
}}"""


class ClaudeAnalyzer:
    def __init__(self):
        settings = get_settings()
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.claude_model
        self.max_tokens = settings.claude_max_tokens

    async def analyse(
        self,
        content: str,
        platform: str,
        nlp_features: dict,
        author_followers: int | None = None,
        author_avg_engagement: float | None = None,
    ) -> dict:
        author_context = ""
        if author_followers is not None:
            author_context = f"AUTHOR CONTEXT: {author_followers:,} followers"
            if author_avg_engagement is not None:
                author_context += f", {author_avg_engagement:.1f}% avg engagement rate"

        prompt = ANALYSIS_PROMPT.format(
            content=content[:5000],  # cap to avoid token overflow
            platform=platform,
            nlp_features=json.dumps(nlp_features, indent=2),
            author_context=author_context,
        )

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text.strip()
            # Strip markdown fences if Claude wraps them
            response_text = response_text.removeprefix("```json").removesuffix("```").strip()

            return json.loads(response_text)

        except json.JSONDecodeError as e:
            # Fallback: return error with raw response for debugging
            return {
                "error": f"Failed to parse Claude response: {str(e)}",
                "raw_response": response_text[:500] if response_text else "",
            }
        except anthropic.APIError as e:
            return {"error": f"Claude API error: {str(e)}"}
