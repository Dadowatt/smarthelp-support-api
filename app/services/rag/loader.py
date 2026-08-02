from functools import lru_cache
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer

from app.core.config import RAG_MODEL_NAME
import re

BASE_DIR = Path(__file__).resolve().parent.parent.parent
KNOWLEDGE_FILE = BASE_DIR / "knowledge" / "support_policy.txt"



def load_documents():
    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        content = file.read()

    rules = re.findall(
        r'- Règle.*?Statut associé\s*:\s*".*?"\.',
        content,
        flags=re.DOTALL,
    )

    documents = []

    for rule in rules:
        status_match = re.search(
            r'Statut associé\s*:\s*"(.*?)"',
            rule,
        )

        status = None

        if status_match:
            status = status_match.group(1)

        documents.append(
            {
                "content": rule.strip(),
                "status": status,
            }
        )

    return documents


@lru_cache(maxsize=1)
def load_rag_model():
    print(">>> Chargement du modèle RAG...")

    model = SentenceTransformer(RAG_MODEL_NAME)

    documents = load_documents()

    texts = [
        doc["content"]
        for doc in documents
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    return {
        "model": model,
        "documents": documents,
        "index": index,
    }