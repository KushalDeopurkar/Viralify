"use client";

import { motion } from "framer-motion";
import { CheckCircle, XCircle, Lightbulb, Quote } from "lucide-react";
import type { Suggestion } from "@/lib/types";

interface Props {
  strengths: string[];
  weaknesses: string[];
  suggestions: Suggestion[];
  rewrittenHook: string | null;
  thumbnailSuggestions: string | null;
}

const PRIORITY_CONFIG = {
  high: {
    bg: "rgba(239, 68, 68, 0.06)",
    border: "rgba(239, 68, 68, 0.15)",
    text: "#EF4444",
    label: "High priority",
  },
  medium: {
    bg: "rgba(245, 158, 11, 0.06)",
    border: "rgba(245, 158, 11, 0.15)",
    text: "#F59E0B",
    label: "Medium",
  },
  low: {
    bg: "rgba(124, 58, 237, 0.06)",
    border: "rgba(124, 58, 237, 0.12)",
    text: "#7C3AED",
    label: "Nice to have",
  },
};

export default function Suggestions({
  strengths,
  weaknesses,
  suggestions,
  rewrittenHook,
  thumbnailSuggestions,
}: Props) {
  return (
    <div className="space-y-4">
      {/* Strengths / Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <motion.div
          initial={{ opacity: 0, x: -12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
          className="glass-card-static p-5"
          style={{ borderColor: "rgba(132, 204, 22, 0.15)" }}
        >
          <h3 className="text-sm font-semibold text-[#84CC16] mb-3 flex items-center gap-2">
            <CheckCircle size={15} /> Strengths
          </h3>
          <ul className="space-y-2.5">
            {strengths.map((s, i) => (
              <li key={i} className="text-sm text-[var(--text-secondary)] flex items-start gap-2.5">
                <span className="text-[#84CC16] mt-0.5 text-xs">+</span>
                <span className="leading-relaxed">{s}</span>
              </li>
            ))}
          </ul>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 12 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="glass-card-static p-5"
          style={{ borderColor: "rgba(239, 68, 68, 0.15)" }}
        >
          <h3 className="text-sm font-semibold text-[#EF4444] mb-3 flex items-center gap-2">
            <XCircle size={15} /> Weaknesses
          </h3>
          <ul className="space-y-2.5">
            {weaknesses.map((w, i) => (
              <li key={i} className="text-sm text-[var(--text-secondary)] flex items-start gap-2.5">
                <span className="text-[#EF4444] mt-0.5 text-xs">−</span>
                <span className="leading-relaxed">{w}</span>
              </li>
            ))}
          </ul>
        </motion.div>
      </div>

      {/* Suggestion cards */}
      <div className="space-y-3">
        {suggestions.map((s, i) => {
          const config = PRIORITY_CONFIG[s.priority];
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 + i * 0.1 }}
              className="p-4 rounded-2xl"
              style={{ background: config.bg, border: `1px solid ${config.border}` }}
            >
              <div className="flex items-start gap-3">
                <Lightbulb size={15} className="mt-0.5 shrink-0" style={{ color: config.text }} />
                <div className="flex-1">
                  <span
                    className="text-[10px] font-semibold uppercase tracking-wider"
                    style={{ color: config.text, opacity: 0.7 }}
                  >
                    {config.label}
                  </span>
                  <p className="text-sm text-[var(--text-primary)] mt-1 leading-relaxed">{s.text}</p>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Rewritten hook */}
      {rewrittenHook && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.9 }}
          className="gradient-border"
        >
          <div className="p-5 relative z-10">
            <div className="flex items-center gap-2 mb-3">
              <Quote size={14} className="text-[var(--accent-violet)]" />
              <h3 className="text-sm font-semibold text-[var(--accent-violet)]">Rewritten hook</h3>
            </div>
            <p className="text-sm text-[var(--text-primary)] italic leading-relaxed">
              &ldquo;{rewrittenHook}&rdquo;
            </p>
          </div>
        </motion.div>
      )}

      {/* Thumbnail/visual suggestions */}
      {thumbnailSuggestions && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.95 }}
          className="glass-card-static p-5"
          style={{ borderColor: "rgba(168, 85, 247, 0.15)" }}
        >
          <h3 className="text-sm font-semibold text-purple-400 mb-2">Visual suggestions</h3>
          <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{thumbnailSuggestions}</p>
        </motion.div>
      )}
    </div>
  );
}
