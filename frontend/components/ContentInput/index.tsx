"use client";

import { FileText, Image as ImageIcon, Video } from "lucide-react";
import type { ContentType } from "@/lib/types";
import TextInput from "./TextInput";
import ImageUpload from "./ImageUpload";
import VideoUpload from "./VideoUpload";

const TABS: { type: ContentType; label: string; Icon: typeof FileText }[] = [
  { type: "text", label: "Text", Icon: FileText },
  { type: "image", label: "Image", Icon: ImageIcon },
  { type: "video", label: "Video", Icon: Video },
];

interface Props {
  contentType: ContentType;
  onContentTypeChange: (type: ContentType) => void;
  text: string;
  onTextChange: (text: string) => void;
  imageFile: File | null;
  onImageChange: (file: File | null) => void;
  videoFile: File | null;
  onVideoChange: (file: File | null) => void;
}

export default function ContentInput({
  contentType,
  onContentTypeChange,
  text,
  onTextChange,
  imageFile,
  onImageChange,
  videoFile,
  onVideoChange,
}: Props) {
  return (
    <div className="space-y-4">
      <div className="flex gap-1 p-1 bg-[var(--bg-card)] rounded-xl w-fit border border-[var(--border-subtle)]">
        {TABS.map(({ type, label, Icon }) => (
          <button
            key={type}
            onClick={() => onContentTypeChange(type)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
              ${
                contentType === type
                  ? "bg-[var(--accent-violet)]/15 text-[var(--accent-violet)]"
                  : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
              }`}
          >
            <Icon size={15} />
            {label}
          </button>
        ))}
      </div>

      {contentType === "text" && <TextInput value={text} onChange={onTextChange} />}
      {contentType === "image" && <ImageUpload file={imageFile} onChange={onImageChange} />}
      {contentType === "video" && <VideoUpload file={videoFile} onChange={onVideoChange} />}
    </div>
  );
}
