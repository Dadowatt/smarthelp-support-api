from dotenv import load_dotenv
import os

load_dotenv()

# Audio
AUDIO_MODEL_NAME = os.getenv(
    "AUDIO_MODEL_NAME",
    "openai/whisper-base"
)

DEFAULT_LANGUAGE = os.getenv(
    "DEFAULT_LANGUAGE",
    "french"
)

# Vision
VISION_MODEL_NAME = os.getenv(
    "VISION_MODEL_NAME",
    "openai/clip-vit-base-patch32"
)

# RAG
RAG_MODEL_NAME = os.getenv(
    "RAG_MODEL_NAME",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "openai/gpt-oss-20b:free"
)