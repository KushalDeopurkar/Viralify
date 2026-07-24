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
