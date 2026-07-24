"use client";

import { motion } from "framer-motion";
import { Clock, Hash, Sparkles } from "lucide-react";

interface Props {
  bestPostingTimes: string[];
  recommendedHashtags: string[];
  emotionsDetected: string[];
}

export default function RecommendationsBar({
  bestPostingTimes,
  recommendedHashtags,
  emotionsDetected,
}: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1 }}
      className="grid grid-cols-1 md:grid-cols-3 gap-4"
    >
      <div className="glass-card-static p-5">
        <h3 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-3 flex items-center gap-2">
          <Clock size={13} /> Best times to post
        </h3>
        <div className="space-y-1.5">
          {bestPostingTimes.map((t, i) => (
            <p key={i} className="text-sm text-[var(--text-secondary)]">{t}</p>
          ))}
        </div>
      </div>

      <div className="glass-card-static p-5">
        <h3 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-3 flex items-center gap-2">
          <Hash size={13} /> Hashtags
        </h3>
        <div className="flex flex-wrap gap-1.5">
          {recommendedHashtags.map((tag, i) => (
            <span
              key={i}
              className="tag-pill border-[var(--accent-violet)]/20 bg-[var(--accent-violet)]/8 text-[var(--accent-violet)]"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>

      <div className="glass-card-static p-5">
        <h3 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider mb-3 flex items-center gap-2">
          <Sparkles size={13} /> Emotions detected
        </h3>
        <div className="flex flex-wrap gap-1.5">
          {emotionsDetected.map((e, i) => (
            <span
              key={i}
              className="tag-pill border-[var(--accent-coral)]/20 bg-[var(--accent-coral)]/8 text-[var(--accent-coral)]"
            >
              {e}
            </span>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
