"use client";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

export default function TextInput({ value, onChange }: Props) {
  const wordCount = value.trim() ? value.trim().split(/\s+/).length : 0;
  const charCount = value.length;

  return (
    <div className="relative">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Paste your content here — a tweet, LinkedIn post, caption, blog intro, video script..."
        className="w-full h-48 p-4 pb-10 bg-[var(--bg-card)] border border-[var(--border-subtle)] rounded-2xl text-[var(--text-primary)] placeholder-[var(--text-muted)] resize-none focus:outline-none focus:ring-2 focus:ring-[var(--accent-violet)]/40 focus:border-[var(--accent-violet)]/40 transition-all text-sm leading-relaxed"
      />
      <div className="absolute bottom-3 right-4 flex gap-3 text-[11px] text-[var(--text-muted)]">
        <span>{wordCount} words</span>
        <span className="opacity-40">·</span>
        <span>{charCount} chars</span>
      </div>
    </div>
  );
}
