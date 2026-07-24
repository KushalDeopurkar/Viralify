"use client";

import type { Platform } from "@/lib/types";

const PLATFORMS: { value: Platform; label: string; icon: string }[] = [
  { value: "twitter", label: "Twitter/X", icon: "𝕏" },
  { value: "linkedin", label: "LinkedIn", icon: "in" },
  { value: "instagram", label: "Instagram", icon: "📸" },
  { value: "tiktok", label: "TikTok", icon: "♪" },
  { value: "reddit", label: "Reddit", icon: "⬆" },
  { value: "youtube", label: "YouTube", icon: "▶" },
  { value: "blog", label: "Blog", icon: "✍" },
  { value: "general", label: "General", icon: "🌐" },
];

interface Props {
  selected: Platform;
  onChange: (platform: Platform) => void;
}

export default function PlatformSelector({ selected, onChange }: Props) {
  return (
    <div>
      <label className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider mb-2 block">
        Target platform
      </label>
      <div className="flex flex-wrap gap-2">
        {PLATFORMS.map((p) => (
          <button
            key={p.value}
            onClick={() => onChange(p.value)}
            className={`px-3.5 py-2 rounded-xl text-sm font-medium transition-all duration-200
              ${
                selected === p.value
                  ? "bg-[var(--accent-violet)] text-white shadow-lg shadow-[var(--accent-violet)]/20"
                  : "bg-[var(--bg-card)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] border border-[var(--border-subtle)] hover:border-[var(--border-hover)]"
              }`}
          >
            <span className="mr-1.5 text-xs">{p.icon}</span>
            {p.label}
          </button>
        ))}
      </div>
    </div>
  );
}
