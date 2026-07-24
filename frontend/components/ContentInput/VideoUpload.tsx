"use client";

import { useCallback, useState, useRef } from "react";
import { Upload, X, Video } from "lucide-react";

interface Props {
  file: File | null;
  onChange: (file: File | null) => void;
}

export default function VideoUpload({ file, onChange }: Props) {
  const [dragOver, setDragOver] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  const handleFile = useCallback(
    (f: File) => { onChange(f); },
    [onChange]
  );

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        const f = e.dataTransfer.files[0];
        if (f?.type.startsWith("video/")) handleFile(f);
      }}
      className={`relative rounded-2xl border-2 border-dashed transition-all duration-200
        ${dragOver
          ? "border-[var(--accent-violet)] bg-[var(--accent-violet)]/5"
          : file
          ? "border-[var(--border-subtle)] bg-[var(--bg-card)]"
          : "border-[var(--border-subtle)] bg-[var(--bg-card)] hover:border-[var(--border-hover)]"
        }`}
    >
      {file ? (
        <div className="relative p-4">
          <video
            ref={videoRef}
            src={URL.createObjectURL(file)}
            className="max-h-48 mx-auto rounded-xl"
            controls
          />
          <button
            onClick={() => onChange(null)}
            className="absolute top-3 right-3 p-1.5 rounded-full bg-black/60 text-white hover:bg-black/80 transition-colors"
          >
            <X size={14} />
          </button>
          <p className="text-xs text-[var(--text-muted)] text-center mt-3">{file.name}</p>
        </div>
      ) : (
        <label className="flex flex-col items-center justify-center h-48 cursor-pointer">
          <div className="w-12 h-12 rounded-2xl bg-[var(--accent-coral)]/10 flex items-center justify-center mb-3">
            <Video size={20} className="text-[var(--accent-coral)]" />
          </div>
          <p className="text-sm text-[var(--text-secondary)]">
            Drop a video or <span className="text-[var(--accent-coral)] font-medium">browse</span>
          </p>
          <p className="text-[11px] text-[var(--text-muted)] mt-1">MP4, MOV, WebM up to 50MB (60s max)</p>
          <input
            type="file"
            accept="video/*"
            className="hidden"
            onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
          />
        </label>
      )}
    </div>
  );
}
