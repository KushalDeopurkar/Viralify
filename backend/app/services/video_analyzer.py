import io
import os
import tempfile
import subprocess

import numpy as np
from PIL import Image

from app.models.schemas import VideoFeatures, CvFeatures, NlpFeatures
from app.services.image_analyzer import analyse_image
from app.services.nlp_analyzer import analyse_text
from app.services.whisper_client import transcribe_audio


def _get_video_duration(video_path: str) -> float:
    """Get video duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", video_path,
            ],
            capture_output=True, text=True, timeout=10,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def extract_keyframes(video_path: str, n_frames: int = 5) -> list[bytes]:
    """Extract n evenly-spaced keyframes from video as JPEG bytes."""
    duration = _get_video_duration(video_path)
    if duration <= 0:
        return []

    frames = []
    with tempfile.TemporaryDirectory() as tmpdir:
        for i in range(n_frames):
            timestamp = duration * (i + 0.5) / n_frames  # center of each segment
            output_path = os.path.join(tmpdir, f"frame_{i}.jpg")
            try:
                subprocess.run(
                    [
                        "ffmpeg", "-ss", str(timestamp), "-i", video_path,
                        "-frames:v", "1", "-q:v", "2", output_path,
                        "-y", "-loglevel", "quiet",
                    ],
                    timeout=10, check=True,
                )
                with open(output_path, "rb") as f:
                    frames.append(f.read())
            except Exception:
                continue
    return frames


def extract_audio(video_path: str) -> str:
    """Extract audio from video as WAV file. Returns path to WAV or empty string."""
    try:
        audio_path = video_path + ".wav"
        subprocess.run(
            [
                "ffmpeg", "-i", video_path, "-vn", "-acodec", "pcm_s16le",
                "-ar", "16000", "-ac", "1", audio_path,
                "-y", "-loglevel", "quiet",
            ],
            timeout=30, check=True,
        )
        return audio_path
    except Exception:
        return ""


def select_top_keyframes(frames: list[bytes], n: int = 3) -> list[bytes]:
    """Select the n most visually diverse keyframes by histogram distance."""
    if len(frames) <= n:
        return frames

    histograms = []
    for frame_bytes in frames:
        try:
            img = Image.open(io.BytesIO(frame_bytes)).convert("L")
            arr = np.array(img)
            hist, _ = np.histogram(arr.flatten(), bins=64, range=(0, 256))
            hist = hist.astype(float) / hist.sum()
            histograms.append(hist)
        except Exception:
            histograms.append(np.zeros(64))

    # Compute pairwise distances to mean histogram
    mean_hist = np.mean(histograms, axis=0)
    distances = [np.sum(np.abs(h - mean_hist)) for h in histograms]

    # Pick n frames with highest variance from mean (most distinctive)
    sorted_indices = sorted(range(len(distances)), key=lambda i: -distances[i])
    selected = sorted(sorted_indices[:n])  # maintain temporal order
    return [frames[i] for i in selected]


def analyse_video(video_bytes: bytes, platform: str) -> tuple[VideoFeatures, list[bytes]]:
    """Full video analysis pipeline. Returns (features, keyframe_bytes_for_gemini)."""
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(video_bytes)
        video_path = tmp.name

    try:
        duration = _get_video_duration(video_path)

        # Step 1: Extract keyframes
        n_frames = 5 if duration >= 3 else max(1, int(duration))
        all_frames = extract_keyframes(video_path, n_frames)

        # Step 2: Extract and transcribe audio
        audio_path = extract_audio(video_path)
        transcript = ""
        has_audio = False
        if audio_path and os.path.exists(audio_path):
            has_audio = os.path.getsize(audio_path) > 1000  # >1KB = has real audio
            if has_audio:
                transcript = transcribe_audio(audio_path)
            try:
                os.unlink(audio_path)
            except OSError:
                pass

        # Step 3: Analyse each keyframe with image pipeline
        keyframe_cv_features = []
        for frame_bytes in all_frames:
            try:
                cv_feat = analyse_image(frame_bytes)
                keyframe_cv_features.append(cv_feat)
            except Exception:
                pass

        # Step 4: Analyse transcript with text pipeline
        transcript_nlp = None
        if transcript:
            transcript_nlp = analyse_text(transcript, platform)

        # Select top 3 for Gemini
        top_frames = select_top_keyframes(all_frames, n=3)

        features = VideoFeatures(
            duration_seconds=round(duration, 1),
            keyframe_count=len(all_frames),
            transcript=transcript,
            has_audio=has_audio,
            keyframe_cv_features=keyframe_cv_features,
            transcript_nlp_features=transcript_nlp,
        )

        return features, top_frames
    finally:
        try:
            os.unlink(video_path)
        except OSError:
            pass
