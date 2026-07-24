"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, Zap, Sparkles } from "lucide-react";
import { analyseContent, type AnalysisResult } from "@/lib/api";
import ViralScore from "@/components/ViralScore";
import DimensionChart from "@/components/DimensionChart";
import Suggestions from "@/components/Suggestions";

const PLATFORMS = [
  { value: "twitter", label: "Twitter / X" },
  { value: "linkedin", label: "LinkedIn" },
  { value: "instagram", label: "Instagram" },
  { value: "tiktok", label: "TikTok" },
  { value: "reddit", label: "Reddit" },
  { value: "youtube", label: "YouTube" },
  { value: "blog", label: "Blog post" },
  { value: "general", label: "General" },
];

export default function AnalysePage() {
  const [content, setContent] = useState("");
  const [platform, setPlatform] = useState("general");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState("");

  const handleAnalyse = async () => {
    if (content.trim().length < 10) {
      setError("Content must be at least 10 characters");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const data = await analyseContent({ content, platform });
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Analysis failed. Check your connection.");
    } finally {
      setLoading(false);
    }
  };

  const charCount = content.length;
  const wordCount = content.trim().split(/\s+/).filter(Boolean).length;

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <Sparkles className="w-8 h-8 text-indigo-500" />
            Viralify
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Predict if your content will go viral
          </p>
        </div>

        {/* Input section */}
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 mb-6">
          {/* Platform selector */}
          <div className="flex flex-wrap gap-2 mb-4">
            {PLATFORMS.map((p) => (
              <button
                key={p.value}
                onClick={() => setPlatform(p.value)}
                className={`px-3 py-1.5 text-sm rounded-lg transition-all ${
                  platform === p.value
                    ? "bg-indigo-100 dark:bg-indigo-900/40 text-indigo-700 dark:text-indigo-300 font-medium"
                    : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700"
                }`}
              >
                {p.label}
              </button>
            ))}
          </div>

          {/* Content textarea */}
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Paste your content here — tweet, LinkedIn post, blog intro, video script, headline..."
            rows={8}
            className="w-full px-4 py-3 text-sm bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl resize-y focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-gray-900 dark:text-white placeholder-gray-400"
          />

          {/* Footer: char count + analyse button */}
          <div className="flex items-center justify-between mt-3">
            <div className="text-xs text-gray-500 dark:text-gray-400 space-x-3">
              <span>{charCount} chars</span>
              <span>{wordCount} words</span>
            </div>

            <button
              onClick={handleAnalyse}
              disabled={loading || content.trim().length < 10}
              className="inline-flex items-center gap-2 px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 dark:disabled:bg-gray-700 text-white text-sm font-medium rounded-xl transition-colors"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Analysing...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  Analyse
                </>
              )}
            </button>
          </div>

          {error && (
            <p className="text-sm text-red-600 dark:text-red-400 mt-3">{error}</p>
          )}
        </div>

        {/* Loading state */}
        <AnimatePresence>
          {loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-12 flex flex-col items-center gap-4"
            >
              <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
              <p className="text-gray-600 dark:text-gray-400">
                Running NLP analysis and STEPPS evaluation...
              </p>
              <p className="text-xs text-gray-400 dark:text-gray-500">
                This takes 3-5 seconds
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results */}
        <AnimatePresence>
          {result && !loading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              {/* Score + chart row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Viral score */}
                <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6 flex items-center justify-center">
                  <ViralScore
                    score={result.overall_score}
                    verdict={result.verdict}
                    confidence={result.confidence}
                  />
                </div>

                {/* Dimension chart */}
                <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6">
                  <h2 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-4">
                    Dimension breakdown
                  </h2>
                  <DimensionChart scores={result.dimension_scores} />
                </div>
              </div>

              {/* Quick stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {result.emotions_detected.slice(0, 2).map((emotion, i) => (
                  <div
                    key={i}
                    className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4"
                  >
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Detected emotion
                    </p>
                    <p className="text-sm font-semibold text-gray-900 dark:text-white capitalize mt-1">
                      {emotion}
                    </p>
                  </div>
                ))}
                <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4">
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Readability
                  </p>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white mt-1">
                    {result.nlp_features.readability.difficulty}
                  </p>
                </div>
                <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-4">
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Platform fit
                  </p>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white mt-1">
                    {result.nlp_features.platform_fit.overall_platform_score}/100
                  </p>
                </div>
              </div>

              {/* Suggestions */}
              <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6">
                <Suggestions
                  suggestions={result.suggestions}
                  strengths={result.strengths}
                  weaknesses={result.weaknesses}
                  rewrittenHook={result.rewritten_hook}
                />
              </div>

              {/* Hashtags & timing */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6">
                  <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                    Recommended hashtags
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {result.recommended_hashtags.map((tag, i) => (
                      <span
                        key={i}
                        className="px-3 py-1 text-sm bg-indigo-50 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded-full"
                      >
                        #{tag.replace(/^#/, "")}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6">
                  <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                    Best posting times
                  </h3>
                  <ul className="space-y-2">
                    {result.best_posting_times.map((time, i) => (
                      <li
                        key={i}
                        className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2"
                      >
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 shrink-0" />
                        {time}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
