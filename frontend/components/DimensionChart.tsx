"use client";

import { motion } from "framer-motion";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import type { DimensionScores } from "@/lib/types";

interface Props {
  scores: DimensionScores;
}

const DIMENSION_LABELS: Record<string, string> = {
  emotional_impact: "Emotion",
  social_currency: "Social currency",
  practical_value: "Practical value",
  narrative_strength: "Narrative",
  trigger_potential: "Triggers",
  shareability: "Shareability",
  platform_fit: "Platform fit",
  hook_quality: "Hook",
};

function getScoreColor(score: number): string {
  if (score >= 70) return "#84CC16";
  if (score >= 50) return "#F59E0B";
  return "#EF4444";
}

export default function DimensionChart({ scores }: Props) {
  const data = Object.entries(scores).map(([key, val]) => ({
    dimension: DIMENSION_LABELS[key] || key,
    score: val.score,
    detail: val.detail,
    fullMark: 100,
  }));

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.6, delay: 0.3 }}
    >
      <ResponsiveContainer width="100%" height={300}>
        <RadarChart data={data} cx="50%" cy="50%" outerRadius="72%">
          <PolarGrid stroke="rgba(124, 58, 237, 0.08)" />
          <PolarAngleAxis
            dataKey="dimension"
            tick={{ fill: "var(--text-secondary)", fontSize: 11 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={false}
            axisLine={false}
          />
          <Radar
            name="Score"
            dataKey="score"
            stroke="#7C3AED"
            fill="url(#radarGrad)"
            fillOpacity={1}
            strokeWidth={2}
          />
          <defs>
            <radialGradient id="radarGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#7C3AED" stopOpacity={0.3} />
              <stop offset="100%" stopColor="#7C3AED" stopOpacity={0.05} />
            </radialGradient>
          </defs>
          <Tooltip
            content={({ payload }) => {
              if (!payload?.length) return null;
              const d = payload[0].payload;
              return (
                <div className="bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-xl p-3 text-sm max-w-xs shadow-xl">
                  <p className="font-semibold text-[var(--text-primary)]">
                    {d.dimension}: <span style={{ color: getScoreColor(d.score) }}>{d.score}</span>
                  </p>
                  <p className="text-[var(--text-secondary)] mt-1 text-xs leading-relaxed">{d.detail}</p>
                </div>
              );
            }}
          />
        </RadarChart>
      </ResponsiveContainer>

      <div className="grid grid-cols-2 gap-1.5 mt-3">
        {data.map((d) => (
          <div
            key={d.dimension}
            className="flex items-center justify-between px-3 py-2 rounded-xl bg-[var(--bg-card)] border border-[var(--border-subtle)]"
          >
            <span className="text-xs text-[var(--text-secondary)]">{d.dimension}</span>
            <span
              className="text-sm font-semibold tabular-nums"
              style={{ color: getScoreColor(d.score) }}
            >
              {d.score}
            </span>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
