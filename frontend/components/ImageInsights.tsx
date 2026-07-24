"use client";

import { motion } from "framer-motion";
import { Image as ImageIcon, Users, Sun, Grid3X3 } from "lucide-react";
import type { CvFeatures } from "@/lib/types";

interface Props {
  features: CvFeatures;
}

export default function ImageInsights({ features }: Props) {
  const stats = [
    { icon: ImageIcon, label: "Dimensions", value: `${features.width}×${features.height}` },
    { icon: Users, label: "Faces", value: String(features.face_count) },
    { icon: Sun, label: "Brightness", value: String(Math.round(features.brightness_score)) },
    { icon: Grid3X3, label: "Composition", value: String(Math.round(features.composition_score)) },
  ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.5 }}
      className="glass-card-static p-5 space-y-4"
    >
      <h3 className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
        Image analysis
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {stats.map(({ icon: Icon, label, value }) => (
          <div key={label} className="text-center p-3 rounded-xl bg-[var(--bg-primary)]/50">
            <Icon size={14} className="mx-auto mb-2 text-[var(--text-muted)]" />
            <p className="text-xl font-bold text-[var(--text-primary)] tabular-nums">{value}</p>
            <p className="text-[11px] text-[var(--text-muted)] mt-0.5">{label}</p>
          </div>
        ))}
      </div>
      {features.dominant_colors.length > 0 && (
        <div>
          <p className="text-[11px] text-[var(--text-muted)] mb-2">Dominant colors</p>
          <div className="flex gap-2">
            {features.dominant_colors.slice(0, 5).map((c, i) => (
              <div
                key={i}
                className="w-8 h-8 rounded-lg border border-white/5 shadow-inner"
                style={{ backgroundColor: `rgb(${c[0]}, ${c[1]}, ${c[2]})` }}
                title={`RGB(${c[0]}, ${c[1]}, ${c[2]})`}
              />
            ))}
          </div>
        </div>
      )}
      {features.has_text_overlay && features.detected_text && (
        <div className="text-xs text-[var(--text-secondary)] p-3 rounded-xl bg-[var(--bg-primary)]/50">
          Text detected: &ldquo;{features.detected_text.slice(0, 100)}&rdquo;
        </div>
      )}
    </motion.div>
  );
}
