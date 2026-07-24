"use client";

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import type { DimensionScore } from "@/lib/api";

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

interface DimensionChartProps {
  scores: Record<string, DimensionScore>;
}

export default function DimensionChart({ scores }: DimensionChartProps) {
  const data = Object.entries(scores).map(([key, val]) => ({
    dimension: DIMENSION_LABELS[key] || key,
    score: val.score,
    detail: val.detail,
    fullMark: 100,
  }));

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={320}>
        <RadarChart data={data} cx="50%" cy="50%" outerRadius="75%">
          <PolarGrid stroke="#e5e7eb" />
          <PolarAngleAxis
            dataKey="dimension"
            tick={{ fontSize: 12, fill: "#6b7280" }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fontSize: 10 }}
          />
          <Tooltip
            content={({ payload }) => {
              if (!payload?.length) return null;
              const d = payload[0].payload;
              return (
                <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-3 shadow-lg text-sm max-w-xs">
                  <p className="font-semibold">{d.dimension}: {d.score}/100</p>
                  <p className="text-gray-600 dark:text-gray-300 mt-1">{d.detail}</p>
                </div>
              );
            }}
          />
          <Radar
            dataKey="score"
            stroke="#6366f1"
            fill="#6366f1"
            fillOpacity={0.2}
            strokeWidth={2}
          />
        </RadarChart>
      </ResponsiveContainer>

      {/* Score list below chart */}
      <div className="grid grid-cols-2 gap-2 mt-4">
        {data.map((d) => (
          <div
            key={d.dimension}
            className="flex items-center justify-between px-3 py-2 rounded-lg bg-gray-50 dark:bg-gray-800/50"
          >
            <span className="text-sm text-gray-600 dark:text-gray-400">
              {d.dimension}
            </span>
            <span
              className="text-sm font-semibold tabular-nums"
              style={{
                color:
                  d.score >= 70
                    ? "#10b981"
                    : d.score >= 50
                    ? "#3b82f6"
                    : d.score >= 30
                    ? "#f59e0b"
                    : "#ef4444",
              }}
            >
              {d.score}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
