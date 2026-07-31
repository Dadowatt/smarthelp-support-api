from app.services.audio.loader import load_whisper_model


def transcribe_audio(audio_path: str) -> str:
    model = load_whisper_model()

    result = model(audio_path)

    return result["text"]