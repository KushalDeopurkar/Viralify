import io
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from app.services.whisper_client import transcribe_audio
from app.services.video_analyzer import (
    extract_keyframes,
    extract_audio,
    select_top_keyframes,
    analyse_video,
)


class TestWhisperClient:
    @patch("app.services.whisper_client.Groq")
    def test_transcribe_returns_text(self, mock_groq_cls):
        mock_client = MagicMock()
        mock_groq_cls.return_value = mock_client
        mock_transcription = MagicMock()
        mock_transcription.text = "Hello everyone welcome to my channel"
        mock_client.audio.transcriptions.create.return_value = mock_transcription

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"fake audio bytes")
            audio_path = f.name
        try:
            result = transcribe_audio(audio_path)
        finally:
            os.unlink(audio_path)
        assert result == "Hello everyone welcome to my channel"

    @patch("app.services.whisper_client.Groq")
    def test_transcribe_failure_returns_empty(self, mock_groq_cls):
        mock_client = MagicMock()
        mock_groq_cls.return_value = mock_client
        mock_client.audio.transcriptions.create.side_effect = Exception("API Error")

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(b"fake audio bytes")
            audio_path = f.name
        try:
            result = transcribe_audio(audio_path)
        finally:
            os.unlink(audio_path)
        assert result == ""

    def test_transcribe_missing_file_returns_empty(self):
        result = transcribe_audio("/tmp/does_not_exist_at_all.wav")
        assert result == ""


class TestKeyframeSelection:
    def test_select_top_keyframes_reduces_count(self):
        # Create 5 fake keyframe images of different brightness
        frames = []
        for brightness in [50, 100, 150, 200, 250]:
            import numpy as np
            from PIL import Image
            arr = np.full((100, 100, 3), brightness, dtype=np.uint8)
            img = Image.fromarray(arr)
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            frames.append(buf.getvalue())

        top_3 = select_top_keyframes(frames, n=3)
        assert len(top_3) == 3

    def test_select_returns_all_if_fewer_than_n(self):
        frames = [b"frame1", b"frame2"]
        result = select_top_keyframes(frames, n=3)
        assert len(result) == 2


class TestFfmpegPipeline:
    """Integration tests using a tiny synthetic video generated via FFmpeg."""

    @pytest.fixture
    def tiny_video_bytes(self):
        import subprocess

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "tiny.mp4")
            subprocess.run(
                [
                    "ffmpeg", "-f", "lavfi", "-i",
                    "testsrc=duration=2:size=64x64:rate=5",
                    "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-shortest",
                    video_path, "-y", "-loglevel", "quiet",
                ],
                check=True, timeout=30,
            )
            with open(video_path, "rb") as f:
                yield f.read()

    def test_get_video_duration(self, tiny_video_bytes):
        from app.services.video_analyzer import _get_video_duration

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(tiny_video_bytes)
            path = tmp.name
        try:
            duration = _get_video_duration(path)
        finally:
            os.unlink(path)
        assert duration > 0

    def test_extract_keyframes_returns_jpeg_bytes(self, tiny_video_bytes):
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(tiny_video_bytes)
            path = tmp.name
        try:
            frames = extract_keyframes(path, n_frames=3)
        finally:
            os.unlink(path)
        assert len(frames) == 3
        for frame in frames:
            assert frame.startswith(b"\xff\xd8")  # JPEG magic bytes

    def test_extract_audio_produces_wav_file(self, tiny_video_bytes):
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp.write(tiny_video_bytes)
            path = tmp.name
        try:
            audio_path = extract_audio(path)
            assert audio_path
            assert os.path.exists(audio_path)
            assert os.path.getsize(audio_path) > 1000
        finally:
            os.unlink(path)
            if audio_path and os.path.exists(audio_path):
                os.unlink(audio_path)

    @patch("app.services.whisper_client.Groq")
    def test_analyse_video_full_pipeline(self, mock_groq_cls, tiny_video_bytes):
        mock_client = MagicMock()
        mock_groq_cls.return_value = mock_client
        mock_transcription = MagicMock()
        mock_transcription.text = "This is a test transcript"
        mock_client.audio.transcriptions.create.return_value = mock_transcription

        features, top_frames = analyse_video(tiny_video_bytes, "tiktok")

        assert features.duration_seconds > 0
        assert features.keyframe_count > 0
        assert features.has_audio is True
        assert features.transcript == "This is a test transcript"
        assert features.transcript_nlp_features is not None
        assert len(features.keyframe_cv_features) == features.keyframe_count
        assert len(top_frames) <= 3
        assert len(top_frames) > 0

    def test_analyse_video_no_audio_stream(self):
        import subprocess

        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = os.path.join(tmpdir, "silent.mp4")
            subprocess.run(
                [
                    "ffmpeg", "-f", "lavfi", "-i",
                    "testsrc=duration=2:size=64x64:rate=5",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    video_path, "-y", "-loglevel", "quiet",
                ],
                check=True, timeout=30,
            )
            with open(video_path, "rb") as f:
                video_bytes = f.read()

        features, top_frames = analyse_video(video_bytes, "tiktok")
        assert features.duration_seconds > 0
        assert features.transcript == ""
        assert len(top_frames) > 0
