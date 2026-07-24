"use client";

import { useCallback, useState } from "react";
import { Upload, X, Image as ImageIcon } from "lucide-react";

interface Props {
  file: File | null;
  onChange: (file: File | null) => void;
}

export default function ImageUpload({ file, onChange }: Props) {
  const [dragOver, setDragOver] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);

  const handleFile = useCallback(
    (f: File) => {
      onChange(f);
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result as string);
      reader.readAsDataURL(f);
    },
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
        if (f?.type.startsWith("image/")) handleFile(f);
      }}
      className={`relative rounded-2xl border-2 border-dashed transition-all duration-200
        ${dragOver
          ? "border-[var(--accent-violet)] bg-[var(--accent-violet)]/5"
          : file
          ? "border-[var(--border-subtle)] bg-[var(--bg-card)]"
          : "border-[var(--border-subtle)] bg-[var(--bg-card)] hover:border-[var(--border-hover)]"
        }`}
    >
      {file && preview ? (
        <div className="relative p-4">
          <img src={preview} alt="Preview" className="max-h-48 mx-auto rounded-xl object-contain" />
          <button
            onClick={() => { onChange(null); setPreview(null); }}
            className="absolute top-3 right-3 p-1.5 rounded-full bg-black/60 text-white hover:bg-black/80 transition-colors"
          >
            <X size={14} />
          </button>
          <p className="text-xs text-[var(--text-muted)] text-center mt-3">{file.name}</p>
        </div>
      ) : (
        <label className="flex flex-col items-center justify-center h-48 cursor-pointer">
          <div className="w-12 h-12 rounded-2xl bg-[var(--accent-violet)]/10 flex items-center justify-center mb-3">
            <ImageIcon size={20} className="text-[var(--accent-violet)]" />
          </div>
          <p className="text-sm text-[var(--text-secondary)]">
            Drop an image or <span className="text-[var(--accent-violet)] font-medium">browse</span>
          </p>
          <p className="text-[11px] text-[var(--text-muted)] mt-1">PNG, JPG, WebP up to 10MB</p>
          <input
            type="file"
            accept="image/*"
            className="hidden"
            onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
          />
        </label>
      )}
    </div>
  );
}
