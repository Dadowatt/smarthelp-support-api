from functools import lru_cache

from transformers import pipeline

from app.core.config import MODEL_NAME


@lru_cache(maxsize=1)
def load_whisper_model():
    print(">>> Chargement du modèle Whisper...")
    model = pipeline(
        task="automatic-speech-recognition",
        model=MODEL_NAME,
    )

    return model