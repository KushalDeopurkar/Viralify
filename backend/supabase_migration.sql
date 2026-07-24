-- Run this in Supabase SQL Editor to create tables

-- Users (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT,
    plan TEXT DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'team', 'enterprise')),
    analyses_today INT DEFAULT 0,
    analyses_reset_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Analyses
CREATE TABLE IF NOT EXISTS public.analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    content_text TEXT NOT NULL,
    platform TEXT NOT NULL DEFAULT 'general',
    overall_score INT CHECK (overall_score >= 0 AND overall_score <= 100),
    dimension_scores JSONB DEFAULT '{}',
    nlp_features JSONB DEFAULT '{}',
    suggestions JSONB DEFAULT '[]',
    claude_response JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Feedback for future ML training
CREATE TABLE IF NOT EXISTS public.feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID REFERENCES public.analyses(id) ON DELETE CASCADE,
    actually_went_viral BOOLEAN DEFAULT FALSE,
    actual_engagement JSONB DEFAULT '{}',
    reported_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_analyses_user_id ON public.analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_analyses_created_at ON public.analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analyses_score ON public.analyses(overall_score);
CREATE INDEX IF NOT EXISTS idx_feedback_analysis_id ON public.feedback(analysis_id);

-- RLS Policies
ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.feedback ENABLE ROW LEVEL SECURITY;

-- Users can read/write their own data
CREATE POLICY "Users can view own analyses"
    ON public.analyses FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analyses"
    ON public.analyses FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE
    USING (auth.uid() = id);

-- Allow anonymous analyses (no user_id)
CREATE POLICY "Allow anonymous analyses"
    ON public.analyses FOR INSERT
    WITH CHECK (user_id IS NULL);

CREATE POLICY "Allow anonymous read own session"
    ON public.analyses FOR SELECT
    USING (user_id IS NULL);
