"use client";

import { motion } from "framer-motion";
import { Film, Clock, Volume2, FileText } from "lucide-react";
import type { VideoFeatures } from "@/lib/types";

interface Props {
  features: VideoFeatures;
}

export default function KeyframeTimeline({ features }: Props) {
  const stats = [
    { icon: Clock, label: "Duration", value: `${features.duration_seconds.toFixed(1)}s` },
    { icon: Film, label: "Keyframes", value: String(features.keyframe_count) },
    { icon: Volume2, label: "Audio", value: features.has_audio ? "Yes" : "No" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5 }}
      className="glass-card-static p-5 space-y-4"
    >
      <h3 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
        Video analysis
      </h3>
      <div className="grid grid-cols-3 gap-3">
        {stats.map(({ icon: Icon, label, value }) => (
          <div key={label} className="text-center p-3 rounded-xl bg-[var(--bg-primary)]/50">
            <Icon size={14} className="mx-auto mb-2 text-[var(--text-muted)]" />
            <p className="text-xl font-bold text-[var(--text-primary)] tabular-nums">{value}</p>
            <p className="text-[11px] text-[var(--text-muted)] mt-0.5">{label}</p>
          </div>
        ))}
      </div>
      {features.transcript && (
        <div>
          <div className="flex items-center gap-1.5 mb-2">
            <FileText size={12} className="text-[var(--text-muted)]" />
            <p className="text-[11px] text-[var(--text-muted)]">Transcript</p>
          </div>
          <p className="text-sm text-[var(--text-secondary)] bg-[var(--bg-primary)]/50 rounded-xl p-4 max-h-32 overflow-y-auto leading-relaxed">
            {features.transcript}
          </p>
        </div>
      )}
    </motion.div>
  );
}
