from app.services.audio.loader import load_whisper_model
from app.core.config import DEFAULT_LANGUAGE

def transcribe_audio(audio_path: str) -> str:
    model = load_whisper_model()

    result = model(
    audio_path,
    generate_kwargs={
        "language": DEFAULT_LANGUAGE,
        "task": "transcribe"
        }
    )

    return result["text"]