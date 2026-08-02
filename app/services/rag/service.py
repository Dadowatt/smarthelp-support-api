from app.services.rag.loader import load_rag_model


def extract_status(policy: str):
    """
    Extrait le statut associé depuis une règle RAG.
    Exemple:
    Statut associé : "Remboursable"
    devient:
    Remboursable
    """

    if "Statut associé" not in policy:
        return None

    start = policy.find('Statut associé')

    status_part = policy[start:]

    if '"' in status_part:
        status = status_part.split('"')[1]
        return status

    return None

def prioritize_rule(query: str, results: list):
    query = query.lower()

    priority_rules = [
        (
            "Règle 4.2",
            [
                "pas de photo",
                "sans photo",
                "aucune photo",
                "pas d'image",
                "sans preuve",
            ],
        ),
        (
            "Règle 4.1",
            [
                "tombé",
                "tombée",
                "tombe",
                "chute",
                "est tombé",
                "a chuté",
                "cassé après",
                "mauvaise manipulation",
                "mauvaise utilisation",
                "usure",
            ],
        ),
        (
            "Règle 3.3",
            [
                "perdu",
                "bloqué",
                "bloqué depuis",
            ],
        ),
        (
            "Règle 2.2",
            [
                "pièce manquante",
                "accessoire manquant",
                "il manque une pièce",
            ],
        ),
        (
            "Règle 2.1",
            [
                "mauvais modèle",
                "mauvaise couleur",
                "mauvaise taille",
            ],
        ),
        (
            "Règle 3.2",
            [
                "retard",
                "6 jours",
                "7 jours",
                "8 jours",
            ],
        ),
        (
            "Règle 1.1",
            [
                "cassé",
                "cassée",
                "fissuré",
                "fissurée",
                "endommagé",
                "endommagée",
                "écran",
            ],
        ),
    ]

    # Priorité métier
    for rule, keywords in priority_rules:
        if any(keyword in query for keyword in keywords):
            for result in results:
                if rule in result["policy"]:
                    return result

    # Sinon on garde le résultat FAISS
    return results[0]


def search_policy(query: str):
    rag = load_rag_model()

    model = rag["model"]
    index = rag["index"]
    documents = rag["documents"]

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
    )

    scores, indices = index.search(
        query_embedding,
        k=9,
    )

    results = []

    for score, index in zip(scores[0], indices[0]):
        results.append(
            {
                "policy": documents[index]["content"],
                "status": documents[index]["status"],
                "confidence": round((float(score) + 1) / 2, 2),
            }
        )

    best_result = prioritize_rule(query, results)

    best_result["confidence"] = round(best_result["confidence"], 2)

    return best_result