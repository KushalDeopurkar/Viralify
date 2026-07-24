"use client";

import { motion } from "framer-motion";

interface ViralScoreProps {
  score: number;
  verdict: string;
  confidence: string;
}

function getScoreColor(score: number): string {
  if (score >= 80) return "#10b981"; // green
  if (score >= 60) return "#3b82f6"; // blue
  if (score >= 40) return "#f59e0b"; // amber
  return "#ef4444"; // red
}

function getScoreGradient(score: number): [string, string] {
  if (score >= 80) return ["#10b981", "#059669"];
  if (score >= 60) return ["#3b82f6", "#2563eb"];
  if (score >= 40) return ["#f59e0b", "#d97706"];
  return ["#ef4444", "#dc2626"];
}

export default function ViralScore({ score, verdict, confidence }: ViralScoreProps) {
  const color = getScoreColor(score);
  const [c1, c2] = getScoreGradient(score);
  const circumference = 2 * Math.PI * 90;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center gap-4">
      <div className="relative w-56 h-56">
        <svg viewBox="0 0 200 200" className="w-full h-full -rotate-90">
          <defs>
            <linearGradient id="scoreGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor={c1} />
              <stop offset="100%" stopColor={c2} />
            </linearGradient>
          </defs>
          {/* Background ring */}
          <circle
            cx="100" cy="100" r="90"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-gray-100 dark:text-gray-800"
          />
          {/* Score ring */}
          <motion.circle
            cx="100" cy="100" r="90"
            fill="none"
            stroke="url(#scoreGrad)"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: offset }}
            transition={{ duration: 1.5, ease: "easeOut" }}
          />
        </svg>
        {/* Score number */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span
            className="text-5xl font-bold tabular-nums"
            style={{ color }}
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
          >
            {score}
          </motion.span>
          <span className="text-sm text-gray-500 dark:text-gray-400 mt-1">
            / 100
          </span>
        </div>
      </div>

      <motion.div
        className="text-center"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1 }}
      >
        <p className="text-lg font-semibold" style={{ color }}>
          {verdict}
        </p>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Confidence: {confidence}
        </p>
      </motion.div>
    </div>
  );
}
