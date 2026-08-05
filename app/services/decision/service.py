import json
import httpx

from app.core.config import (
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL,
)


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"



async def decide_ticket(
    description: str | None,
    transcription: str | None,
    vision_result: dict | None,
    policies: list,
):
    """
    Décision finale basée sur :
    - texte client
    - transcription audio
    - analyse vision
    - règles RAG récupérées
    """


    context = f"""

DESCRIPTION CLIENT:
{description}


TRANSCRIPTION AUDIO:
{transcription}


ANALYSE IMAGE:
{vision_result}


REGLES TROUVEES PAR LE RAG:
{policies}

"""


    prompt = f"""

Tu es un agent expert du support client.

Analyse le dossier client ci-dessous.

Tu dois choisir UNE SEULE règle parmi les règles fournies par le RAG.

Tu ne dois jamais inventer une nouvelle règle.


Contexte dossier:

{context}


Consignes :

- Une chute après réception correspond à une mauvaise utilisation.
- Une casse visible avec preuve photo et sans mauvaise manipulation correspond à une casse à la livraison.
- Si les preuves sont insuffisantes, choisir la règle d'attente de justificatifs.


Retourne uniquement un JSON :

{{
    "policy": "nom de la règle choisie",
    "statut_final": "statut associé",
    "resume": "explication courte",
    "action_recommandee": "action support"
}}

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
        "temperature": 0.1,
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


    content = (
        data["choices"][0]
        ["message"]
        ["content"]
    )


    content = content.strip()


    if content.startswith("```json"):
        content = content.replace(
            "```json",
            "",
            1,
        )

    if content.endswith("```"):
        content = content[:-3]


    try:

        return json.loads(
            content.strip()
        )

    except Exception:

        return None