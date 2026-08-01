from functools import lru_cache

from transformers import pipeline

from app.core.config import VISION_MODEL_NAME


@lru_cache(maxsize=1)
def load_clip_model():
    print(">>> Chargement du modèle CLIP...")

    model = pipeline(
        task="zero-shot-image-classification",
        model=VISION_MODEL_NAME,
    )

    return model