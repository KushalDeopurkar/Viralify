from groq import Groq

from app.config import settings


def transcribe_audio(audio_path: str) -> str:
    """Transcribe audio file using Groq Whisper. Returns empty string on failure."""
    try:
        client = Groq(api_key=settings.groq_api_key)
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(audio_path, audio_file.read()),
                model="whisper-large-v3",
                response_format="text",
            )
        return transcription.text if hasattr(transcription, "text") else str(transcription)
    except Exception:
        return ""
