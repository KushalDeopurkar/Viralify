"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, Loader2, Activity } from "lucide-react";

import ContentInput from "@/components/ContentInput";
import PlatformSelector from "@/components/PlatformSelector";
import ViralScore from "@/components/ViralScore";
import DimensionChart from "@/components/DimensionChart";
import Suggestions from "@/components/Suggestions";
import ImageInsights from "@/components/ImageInsights";
import KeyframeTimeline from "@/components/KeyframeTimeline";
import RecommendationsBar from "@/components/RecommendationsBar";

import { analyseContent } from "@/lib/api";
import type { AnalyseResponse, ContentType, Platform } from "@/lib/types";

const LOADING_MESSAGES: Record<ContentType, string[]> = {
  text: [
    "Reading between the lines...",
    "Mapping emotional triggers...",
    "Calibrating viral potential...",
  ],
  image: [
    "Scanning visual composition...",
    "Detecting engagement signals...",
    "Evaluating viral potential...",
  ],
  video: [
    "Extracting keyframes...",
    "Transcribing audio...",
    "Analysing content signals...",
  ],
};

export default function AnalysePage() {
  const [contentType, setContentType] = useState<ContentType>("text");
  const [platform, setPlatform] = useState<Platform>("twitter");
  const [text, setText] = useState("");
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [result, setResult] = useState<AnalyseResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const canAnalyse =
    (contentType === "text" && text.trim().length >= 10) ||
    (contentType === "image" && imageFile !== null) ||
    (contentType === "video" && videoFile !== null);

  async function handleAnalyse() {
    setLoading(true);
    setError(null);
    setResult(null);

    const messages = LOADING_MESSAGES[contentType];
    let msgIdx = 0;
    setLoadingMessage(messages[0]);
    const interval = setInterval(() => {
      msgIdx = (msgIdx + 1) % messages.length;
      setLoadingMessage(messages[msgIdx]);
    }, 2500);

    try {
      const response = await analyseContent({
        contentType,
        platform,
        content: contentType === "text" ? text : undefined,
        file:
          contentType === "image"
            ? imageFile!
            : contentType === "video"
            ? videoFile!
            : undefined,
      });
      setResult(response);
    } catch (e) {
      setError(
        e instanceof Error ? e.message : "Analysis failed. Please try again."
      );
    } finally {
      setLoading(false);
      clearInterval(interval);
    }
  }

  return (
    <div className="min-h-screen">
      {/* Nav */}
      <nav className="sticky top-0 z-50 backdrop-blur-md bg-[var(--bg-primary)]/80 border-b border-[var(--border-subtle)]">
        <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-[var(--accent-violet)] to-[var(--accent-coral)] flex items-center justify-center">
              <Activity size={14} className="text-white" />
            </div>
            <span className="text-lg font-semibold tracking-tight text-[var(--text-primary)]">
              Viralify
            </span>
          </div>
          <span className="text-xs text-[var(--text-muted)] hidden sm:block">
            AI-powered content analysis
          </span>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-5xl mx-auto px-6 py-10">
        {/* Hero heading */}
        <div className="mb-10">
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-[var(--text-primary)]">
            Will it go{" "}
            <span className="bg-gradient-to-r from-[var(--accent-violet)] to-[var(--accent-coral)] bg-clip-text text-transparent">
              viral
            </span>
            ?
          </h1>
          <p className="text-[var(--text-secondary)] mt-2 text-base">
            Paste your content, pick a platform, get a score.
          </p>
        </div>

        {/* Input section */}
        <section className="space-y-5 mb-10">
          <ContentInput
            contentType={contentType}
            onContentTypeChange={(t) => {
              setContentType(t);
              setResult(null);
              setError(null);
            }}
            text={text}
            onTextChange={setText}
            imageFile={imageFile}
            onImageChange={setImageFile}
            videoFile={videoFile}
            onVideoChange={setVideoFile}
          />

          <PlatformSelector selected={platform} onChange={setPlatform} />

          <button
            onClick={handleAnalyse}
            disabled={!canAnalyse || loading}
            className="btn-primary w-full py-3.5 px-6 text-sm flex items-center justify-center gap-2.5"
          >
            {loading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                <span className="animate-pulse">{loadingMessage}</span>
              </>
            ) : (
              <>
                <Zap size={16} />
                Analyse viral potential
              </>
            )}
          </button>
        </section>

        {/* Error */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              className="p-4 rounded-2xl bg-red-500/8 border border-red-500/15 text-red-400 text-sm mb-8"
            >
              {error}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results */}
        <AnimatePresence>
          {result && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.4 }}
            >
              {/* Divider */}
              <div className="flex items-center gap-4 mb-10">
                <div className="h-px flex-1 bg-gradient-to-r from-transparent via-[var(--accent-violet)]/30 to-transparent" />
                <span className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-widest">
                  Results
                </span>
                <div className="h-px flex-1 bg-gradient-to-r from-transparent via-[var(--accent-violet)]/30 to-transparent" />
              </div>

              <div className="space-y-8">
                {/* Score + Chart row */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
                  <div className="glass-card p-8">
                    <ViralScore
                      score={result.overall_score}
                      verdict={result.verdict}
                      confidence={result.confidence}
                    />
                  </div>
                  <div className="glass-card p-6">
                    <DimensionChart scores={result.dimension_scores} />
                  </div>
                </div>

                {/* Content-specific insights */}
                {result.cv_features && result.content_type === "image" && (
                  <ImageInsights features={result.cv_features} />
                )}
                {result.video_features && result.content_type === "video" && (
                  <KeyframeTimeline features={result.video_features} />
                )}

                {/* Suggestions */}
                <Suggestions
                  strengths={result.strengths}
                  weaknesses={result.weaknesses}
                  suggestions={result.suggestions}
                  rewrittenHook={result.rewritten_hook}
                  thumbnailSuggestions={result.thumbnail_suggestions}
                />

                {/* Recommendations */}
                <RecommendationsBar
                  bestPostingTimes={result.best_posting_times}
                  recommendedHashtags={result.recommended_hashtags}
                  emotionsDetected={result.emotions_detected}
                />

                {/* Processing time */}
                <p className="text-xs text-[var(--text-muted)] text-center pb-8">
                  Analysed in {(result.processing_time_ms / 1000).toFixed(1)}s
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
