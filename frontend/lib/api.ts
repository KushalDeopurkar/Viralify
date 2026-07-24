import type { AnalyseResponse, ContentType, Platform } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function analyseContent(params: {
  contentType: ContentType;
  platform: Platform;
  content?: string;
  file?: File;
}): Promise<AnalyseResponse> {
  const formData = new FormData();
  formData.append("content_type", params.contentType);
  formData.append("platform", params.platform);

  if (params.content) {
    formData.append("content", params.content);
  }
  if (params.file) {
    formData.append("file", params.file);
  }

  const resp = await fetch(`${API_URL}/api/analyse`, {
    method: "POST",
    body: formData,
  });

  if (!resp.ok) {
    const error = await resp.json().catch(() => ({ detail: "Analysis failed" }));
    throw new Error(error.detail || `HTTP ${resp.status}`);
  }

  return resp.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const resp = await fetch(`${API_URL}/api/health`);
    return resp.ok;
  } catch {
    return false;
  }
}
