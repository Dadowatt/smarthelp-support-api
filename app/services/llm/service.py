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
    policy_status: str,
):
    """
    Génère un diagnostic structuré JSON à partir
    de la question client et du contexte RAG.
    """
    print("===== APPEL LLM =====")
    
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

Statut extrait de la règle :
{policy_status}

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
- Le statut_final doit correspondre au statut métier fourni si les conditions sont respectées.
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
    print("STATUS =", response.status_code)
    print("BODY =")
    print(response.text)

    if response.status_code != 200:
        print("OpenRouter Error:", response.status_code)
        print(response.text)
        return None

    data = response.json()
    print("DATA =")
    print(json.dumps(data, indent=2))

    content = data["choices"][0]["message"]["content"]

    print("===== REPONSE DU LLM =====")
    print(content)
    print("==========================")

    # Nettoyage des balises Markdown éventuelles
    content = content.strip()

    if content.startswith("```json"):
        content = content.replace("```json", "", 1)

    if content.startswith("```"):
        content = content.replace("```", "", 1)

    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()

    try:
        result = json.loads(content)

        return {
            "resume": result.get(
                "resume",
                result.get("diagnostic"),
            ),
            "statut_final": result.get(
                "statut_final",
                result.get("statut_propose"),
            ),
            "action_recommandee": result.get(
                "action_recommandee",
            ),
        }

    except json.JSONDecodeError:
        return {
            "resume": content,
            "statut_final": None,
            "action_recommandee": None,
        }