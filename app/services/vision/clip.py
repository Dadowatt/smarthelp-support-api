from PIL import Image
from app.services.vision.loader import load_clip_model


LABELS = [
    "a product with a visible defect",
    "a product with a cracked screen",
    "a product that is broken",
    "a product in perfect condition",
    "an unrelated image that does not show a product",
]

def analyze_image(image_path: str):
    model = load_clip_model()

    image = Image.open(image_path)

    results = model(
        image,
        candidate_labels=LABELS,
    )

    print("RESULTATS CLIP :", results)

    top_result = results[0]

    CONFIDENCE_THRESHOLD = 0.80

    if top_result["label"] == "an unrelated image that does not show a product":
        image_relevant = False
    else:
        image_relevant = True

    defect_detected = (
        image_relevant
        and top_result["label"] != "a product in perfect condition"
        and top_result["score"] >= CONFIDENCE_THRESHOLD
    )

    return {
        "label": top_result["label"],
        "confidence": round(top_result["score"], 2),
        "image_relevant": image_relevant,
        "defect_detected": defect_detected,
    }