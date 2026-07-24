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
