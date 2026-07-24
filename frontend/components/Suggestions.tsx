"use client";

import { motion } from "framer-motion";
import { AlertTriangle, ArrowUp, Lightbulb } from "lucide-react";
import type { Suggestion } from "@/lib/api";

const PRIORITY_CONFIG = {
  high: {
    icon: AlertTriangle,
    bg: "bg-red-50 dark:bg-red-900/20",
    border: "border-red-200 dark:border-red-800",
    badge: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-400",
    label: "High priority",
  },
  medium: {
    icon: ArrowUp,
    bg: "bg-amber-50 dark:bg-amber-900/20",
    border: "border-amber-200 dark:border-amber-800",
    badge: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-400",
    label: "Medium",
  },
  low: {
    icon: Lightbulb,
    bg: "bg-blue-50 dark:bg-blue-900/20",
    border: "border-blue-200 dark:border-blue-800",
    badge: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-400",
    label: "Nice to have",
  },
};

interface SuggestionsProps {
  suggestions: Suggestion[];
  strengths: string[];
  weaknesses: string[];
  rewrittenHook: string;
}

export default function Suggestions({
  suggestions,
  strengths,
  weaknesses,
  rewrittenHook,
}: SuggestionsProps) {
  return (
    <div className="space-y-6">
      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-xl border border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20 p-4">
          <h3 className="text-sm font-semibold text-green-700 dark:text-green-400 mb-3">
            Strengths
          </h3>
          <ul className="space-y-2">
            {strengths.map((s, i) => (
              <li key={i} className="text-sm text-green-800 dark:text-green-300 flex gap-2">
                <span className="shrink-0 mt-0.5">✓</span>
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="rounded-xl border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 p-4">
          <h3 className="text-sm font-semibold text-red-700 dark:text-red-400 mb-3">
            Weaknesses
          </h3>
          <ul className="space-y-2">
            {weaknesses.map((w, i) => (
              <li key={i} className="text-sm text-red-800 dark:text-red-300 flex gap-2">
                <span className="shrink-0 mt-0.5">✗</span>
                <span>{w}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Suggestions */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
          Suggestions to boost virality
        </h3>
        {suggestions.map((sug, i) => {
          const config = PRIORITY_CONFIG[sug.priority] || PRIORITY_CONFIG.low;
          const Icon = config.icon;
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.15 }}
              className={`rounded-xl border ${config.border} ${config.bg} p-4 flex gap-3`}
            >
              <Icon className="w-5 h-5 shrink-0 mt-0.5 opacity-60" />
              <div>
                <span className={`inline-block text-xs font-medium px-2 py-0.5 rounded-full mb-1.5 ${config.badge}`}>
                  {config.label}
                </span>
                <p className="text-sm text-gray-800 dark:text-gray-200">
                  {sug.suggestion}
                </p>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Rewritten hook */}
      {rewrittenHook && (
        <div className="rounded-xl border border-indigo-200 dark:border-indigo-800 bg-indigo-50 dark:bg-indigo-900/20 p-4">
          <h3 className="text-sm font-semibold text-indigo-700 dark:text-indigo-400 mb-2">
            Improved opening line
          </h3>
          <p className="text-sm text-indigo-900 dark:text-indigo-200 italic">
            &ldquo;{rewrittenHook}&rdquo;
          </p>
        </div>
      )}
    </div>
  );
}
