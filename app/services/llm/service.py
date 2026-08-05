import json
import httpx

from app.core.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
)


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


async def generate_answer(
    question: str,
    context: str,
):
    """
    Génère un diagnostic structuré JSON à partir
    de la question client et du contexte RAG.
    """

    if not OPENROUTER_API_KEY:
        raise Exception(
            "OPENROUTER_API_KEY non configurée."
        )

    prompt = f"""
Tu es un assistant du service client e-commerce.

Tu dois analyser la demande du client uniquement à partir
du contexte de politique interne fourni.

Contexte de la politique interne :
{context}

Question du client :
{question}

Retourne uniquement un JSON valide avec exactement cette structure :

{{
    "resume": "résumé du problème rencontré par le client",
    "statut_final": "statut final recommandé pour le dossier",
    "action_recommandee": "action suivante à effectuer"
}}

Consignes importantes :
- Utilise uniquement les informations présentes dans le contexte.
- N'invente aucune règle, condition ou procédure.
- Si une information manque, indique qu'elle doit être vérifiée.
- Ne retourne aucun texte avant ou après le JSON.
"""

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.2,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )

    if response.status_code != 200:
        return None

    data = response.json()

    content = data["choices"][0]["message"]["content"]

    try:
        result = json.loads(content)

        return {
            "resume": result.get(
                "resume",
                result.get("diagnostic")
            ),
            "statut_final": result.get(
                "statut_final",
                result.get("statut_propose")
            ),
            "action_recommandee": result.get(
                "action_recommandee"
            ),
        }

    except json.JSONDecodeError:
        return {
            "resume": content,
            "statut_final": None,
            "action_recommandee": None,
        }