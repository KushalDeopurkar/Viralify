"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import type { Confidence } from "@/lib/types";

interface Props {
  score: number;
  verdict: string;
  confidence: Confidence;
}

function getScoreColor(score: number): [string, string] {
  if (score >= 80) return ["#84CC16", "rgba(132, 204, 22, 0.15)"];
  if (score >= 60) return ["#7C3AED", "rgba(124, 58, 237, 0.15)"];
  if (score >= 40) return ["#F59E0B", "rgba(245, 158, 11, 0.12)"];
  return ["#EF4444", "rgba(239, 68, 68, 0.12)"];
}

export default function ViralScore({ score, verdict, confidence }: Props) {
  const [displayScore, setDisplayScore] = useState(0);
  const radius = 76;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (displayScore / 100) * circumference;
  const [color, glow] = getScoreColor(score);

  useEffect(() => {
    let frame = 0;
    const totalFrames = 60;
    const interval = setInterval(() => {
      frame++;
      const progress = frame / totalFrames;
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayScore(Math.round(eased * score));
      if (frame >= totalFrames) clearInterval(interval);
    }, 16);
    return () => clearInterval(interval);
  }, [score]);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="flex flex-col items-center"
    >
      <div className="relative w-52 h-52">
        {/* Outer glow ring */}
        <div
          className={score >= 60 ? "score-glow" : ""}
          style={{
            position: "absolute",
            inset: -4,
            borderRadius: "50%",
            background: `radial-gradient(circle, ${glow}, transparent 70%)`,
          }}
        />

        <svg className="w-full h-full -rotate-90" viewBox="0 0 200 200">
          {/* Track */}
          <circle
            cx="100" cy="100" r={radius}
            fill="none"
            stroke="rgba(255,255,255,0.04)"
            strokeWidth="10"
          />
          {/* Tick marks */}
          {Array.from({ length: 40 }).map((_, i) => {
            const angle = (i / 40) * 360;
            const rad = (angle * Math.PI) / 180;
            const isMajor = i % 10 === 0;
            const innerR = isMajor ? 62 : 65;
            const outerR = 68;
            return (
              <line
                key={i}
                x1={100 + innerR * Math.cos(rad)}
                y1={100 + innerR * Math.sin(rad)}
                x2={100 + outerR * Math.cos(rad)}
                y2={100 + outerR * Math.sin(rad)}
                stroke={isMajor ? "rgba(255,255,255,0.15)" : "rgba(255,255,255,0.06)"}
                strokeWidth={isMajor ? 1.5 : 0.75}
              />
            );
          })}
          {/* Progress arc */}
          <motion.circle
            cx="100" cy="100" r={radius}
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.8, ease: "easeOut" }}
          />
          {/* End cap glow */}
          <motion.circle
            cx="100" cy="100" r={radius}
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.8, ease: "easeOut" }}
            style={{ filter: `blur(6px)` }}
            opacity={0.4}
          />
        </svg>

        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="text-5xl font-bold tabular-nums"
            style={{ color }}
          >
            {displayScore}
          </span>
          <span className="text-[11px] text-[var(--text-muted)] mt-0.5 tracking-wide">
            out of 100
          </span>
        </div>
      </div>

      <p className="mt-4 text-base font-semibold text-[var(--text-primary)]">
        {verdict}
      </p>
      <span className="text-[11px] text-[var(--text-muted)] mt-1.5 px-3 py-1 rounded-full border border-[var(--border-subtle)] bg-[var(--bg-card)]">
        {confidence} confidence
      </span>
    </motion.div>
  );
}
