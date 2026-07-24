const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface AnalyseRequest {
  content: string;
  platform: string;
  author_followers?: number;
  author_avg_engagement?: number;
}

export interface DimensionScore {
  score: number;
  detail: string;
}

export interface Suggestion {
  priority: "high" | "medium" | "low";
  suggestion: string;
}

export interface AnalysisResult {
  overall_score: number;
  verdict: string;
  dimension_scores: Record<string, DimensionScore>;
  emotions_detected: string[];
  strengths: string[];
  weaknesses: string[];
  suggestions: Suggestion[];
  rewritten_hook: string;
  best_posting_times: string[];
  recommended_hashtags: string[];
  nlp_features: {
    readability: Record<string, any>;
    sentiment: Record<string, any>;
    structure: Record<string, any>;
    engagement_signals: Record<string, any>;
    platform_fit: Record<string, any>;
  };
  confidence: string;
}

export interface QuickResult {
  quick_score: number;
  component_scores: Record<string, number>;
  nlp_features: Record<string, any>;
}

export async function analyseContent(
  request: AnalyseRequest
): Promise<AnalysisResult> {
  const res = await fetch(`${API_URL}/api/analyse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Analysis failed" }));
    throw new Error(error.detail || "Analysis failed");
  }

  return res.json();
}

export async function quickAnalyse(
  request: AnalyseRequest
): Promise<QuickResult> {
  const res = await fetch(`${API_URL}/api/analyse/quick`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!res.ok) throw new Error("Quick analysis failed");
  return res.json();
}
