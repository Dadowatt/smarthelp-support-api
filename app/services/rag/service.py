from app.services.rag.loader import load_rag_model
from app.services.llm.service import generate_answer



def extract_status(policy: str):

    if "Statut associé" not in policy:
        return None

    part = policy.split("Statut associé")[1]

    if '"' in part:
        return part.split('"')[1]

    return None



def generate_rag_diagnostic(
    policy: str,
    status: str,
    query: str,
):

    if "Règle 1.1" in policy:

        return {
            "resume": (
                "Le client signale un produit cassé, "
                "fissuré ou endommagé à la réception."
            ),
            "statut_final": status,
            "action_recommandee": (
                "Vérifier que le dommage est signalé "
                "dans les 48 heures avec une preuve."
            ),
        }


    if "Règle 4.1" in policy:

        return {
            "resume": (
                "Le dommage semble lié à une chute, "
                "une mauvaise manipulation ou une usure."
            ),
            "statut_final": status,
            "action_recommandee": (
                "Analyser les circonstances du dommage."
            ),
        }


    if "Règle 4.2" in policy:

        return {
            "resume": (
                "La demande nécessite des justificatifs "
                "complémentaires."
            ),
            "statut_final": status,
            "action_recommandee": (
                "Demander une preuve supplémentaire."
            ),
        }


    if "Règle 3.3" in policy:

        return {
            "resume": (
                "Le client signale un problème "
                "lié au transport."
            ),
            "statut_final": status,
            "action_recommandee": (
                "Vérifier le statut transporteur."
            ),
        }


    if "Règle 2.1" in policy:

        return {
            "resume": (
                "Le client indique avoir reçu "
                "un mauvais article."
            ),
            "statut_final": status,
            "action_recommandee": (
                "Organiser un échange."
            ),
        }


    if "Règle 2.2" in policy:

        return {
            "resume": (
                "Le client signale une pièce manquante."
            ),
            "statut_final": status,
            "action_recommandee": (
                "Envoyer la pièce manquante."
            ),
        }


    return {
        "resume": query,
        "statut_final": status,
        "action_recommandee": (
            "Appliquer la procédure correspondante."
        ),
    }



def select_best_rule(results):

    if not results:
        return None


    return results[0]



async def search_policy(
    query: str,
    has_image: bool = False,
):


    rag = load_rag_model()


    model = rag["model"]
    index = rag["index"]
    documents = rag["documents"]



    embedding = model.encode(
        [query],
        normalize_embeddings=True,
    )


    scores, indices = index.search(
        embedding,
        k=5,
    )



    results = []


    for score, idx in zip(scores[0], indices[0]):

        results.append(
            {
                "policy": documents[idx]["content"],
                "status": documents[idx]["status"],
                "confidence": round(
                    (float(score)+1)/2,
                    2
                )
            }
        )



    best = select_best_rule(results)



    print("======================")
    print("QUESTION RAG")
    print(query)

    print("======================")
    print("REGLE RETENUE")
    print(best["policy"])



    if best["status"]:

        return {

            "policy": best["policy"],

            "confidence": best["confidence"],

            "policy_status": best["status"],

            "diagnostic": generate_rag_diagnostic(
                policy=best["policy"],
                status=best["status"],
                query=query,
            )
        }



    llm_response = await generate_answer(
        question=query,
        context=best["policy"],
        policy_status=best["status"],
    )


    return {

        "policy": best["policy"],

        "confidence": best["confidence"],

        "policy_status": best["status"],

        "diagnostic": llm_response

    }