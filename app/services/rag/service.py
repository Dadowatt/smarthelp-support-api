from app.services.rag.loader import load_rag_model
import unicodedata
import re

def normalize_text(text: str):

    text = text.lower()

    text = unicodedata.normalize(
        "NFD",
        text
    )

    text = "".join(
        c for c in text
        if unicodedata.category(c) != "Mn"
    )

    return text

def extract_rule(policy: str):

    match = re.search(
        r"Règle\s+(\d+\.\d+)",
        policy
    )

    if not match:
        return None

    return match.group(1)


def boost_rule_matching(
    query: str,
    policy: str
):

    query = normalize_text(query)
    policy = normalize_text(policy)

    score = 0

    keywords = {

        "regle 1.1": [
            "cass",
            "fissur",
            "endomm",
            "brise",
            "ecran brise",
            "arrive cass",
            "produit casse",
            "telephone casse",
            "ecran casse",
            "livraison",
            "reception"
        ],

        "regle 4.1": [
            "tomb",
            "chut",
            "mauvaise manipulation",
            "mauvais usage",
            "usure",
            "abime apres reception"
        ],

        "regle 4.2": [
            "pas de photo",
            "sans photo",
            "aucune preuve",
            "pas de preuve",
            "manque preuve",
            "aucun justificatif"
        ],

        "regle 2.1": [
            "mauvais modele",
            "mauvais article",
            "mauvais produit",
            "mauvaise couleur",
            "mauvaise taille",
            "mauvaise reference"
        ],

        "regle 2.2": [
            "piece manquante",
            "accessoire manquant",
            "element manquant",
            "composant manquant",
            "incomplet"
        ],

        "regle 3.1": [
            "retard leger",
            "retard mineur",
            "1 jour",
            "2 jours",
            "3 jours",
            "moins de 3 jours"
        ],

        "regle 3.2": [
            "retard majeur",
            "plus de 5 jours",
            "6 jours",
            "7 jours",
            "plusieurs jours retard",
            "retard important"
        ],

        "regle 3.3": [
            "perdu",
            "colis perdu",
            "bloque",
            "transporteur",
            "suivi bloque",
            "statut perdu",
            "pas arrive",
            "toujours pas arrive",
            "colis pas arrive",
            "commande pas arrivee"
        ],

    }

    for rule, words in keywords.items():

        if rule in policy:

            for word in words:

                if word in query:

                    score += 1

    # =========================
    # PRIORITES METIER
    # =========================

    # Absence de preuve

    if (
        "pas de photo" in query
        or "sans photo" in query
        or "aucune photo" in query
        or "pas de preuve" in query
        or "aucune preuve" in query
    ):

        if "regle 4.2" in policy:
            score += 10
        if "regle 1.1" in policy:
            score -= 5

    # Chute après réception

    if (
        "tombe" in query
        or "tomber" in query
        or "chute" in query
        or "fait tomber" in query
        or "mauvaise manipulation" in query
    ):


        if "regle 4.1" in policy:
            score += 10

        if "regle 1.1" in policy:
            score -= 5

    # Produit cassé dès réception

    if (
        "arrive casse" in query
        or "arrive endommage" in query
        or "a la reception" in query
        or "des reception" in query
    ):
        if "regle 1.1" in policy:
            score += 10
    return score

def calculate_final_confidence(
    faiss_score: float,
    boost: int
):
    confidence = faiss_score + (boost * 0.03)

    if confidence > 0.99:
        confidence = 0.99

    if confidence < 0:
        confidence = 0

    return round(confidence, 2)

def determine_policy_status(
    query: str,
    rule: str | None,
    image_received: bool,
    audio_received: bool,
):
    query_normalized = normalize_text(query)

    # Produit tombé / mauvaise manipulation après réception
    if rule == "4.1":
        return "Refusé", []

    # Colis perdu / bloqué
    if rule == "3.3":
        if (
            "plus de 7 jours" in query_normalized
            or "8 jours" in query_normalized
            or "9 jours" in query_normalized
            or "10 jours" in query_normalized
        ):
            return "Remboursable - Colis perdu", []

        return "À vérifier", [
            "Délai depuis l'expédition ou le dernier suivi"
        ]

    # Règle 1.1 : produit endommagé
    if rule == "1.1":

        # Image + audio = justificatifs complets
        if image_received and audio_received:
            return "Remboursable", []

        # Image + description indiquant un dommage à la réception
        if image_received:
            if "reception" in query_normalized:
                return "Remboursable", []

            return "À vérifier", [
                "Description précise du problème ou message vocal"
            ]

        # Audio seul ou aucun justificatif
        return "En attente de justificatifs", [
            "Photo probante du produit endommagé"
        ]

    # Règle 4.2 : photo ou audio accepté comme preuve
    if rule == "4.2" and not image_received and not audio_received:
        return "En attente de justificatifs", [
            "Photo probante ou message vocal décrivant clairement le problème"
        ]

    return None, []

async def search_policy(
    query: str,
    image_received: bool = False,
    audio_received: bool = False,
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
        if idx < 0:
            continue
        results.append(

            {
                "policy": documents[idx]["content"],
                "status": documents[idx]["status"],
                "confidence": round((float(score) + 1) / 2, 2)
            }
        )

    if not results:
        return None

    for result in results:

        result["boost"] = boost_rule_matching(
            query,
            result["policy"]
        )

    results.sort(
        key=lambda x: (
            x["boost"],
            x["confidence"]
        ),
        reverse=True
    )

    print("\n===== DEBUG BOOST =====")

    for result in results:

        print(
            result["policy"][:40],
            "FAISS:",
            result["confidence"],
            "BOOST:",
            result["boost"]
        )

    print("======================")

    best = results[0]

    # =========================
    # VERIFICATION DU CONTEXTE
    # =========================

    if best["boost"] == 0 and best["confidence"] < 0.70:
        return {
            "policy": None,
            "rule": None,
            "confidence": best["confidence"],
            "policy_status": "Règle introuvable. Veuillez reformuler votre demande.",
            "missing_information": [],
        }

    rule = extract_rule(best["policy"])

    final_confidence = calculate_final_confidence(
        best["confidence"],
        best["boost"]
    )

    policy_status, missing_information = determine_policy_status(
        query,
        rule,
        image_received,
        audio_received,
    )

    if policy_status is None:
        policy_status = best["status"]

    return {
        "policy": best["policy"],
        "rule": rule,
        "confidence": final_confidence,
        "policy_status": policy_status,
        "missing_information": missing_information,
    }