from PIL import Image

from app.services.vision.loader import load_clip_model


LABELS = [
    "a product with a visible defect",
    "a product with a cracked screen",
    "a product that is broken",
    "a product in perfect condition",
]


def analyze_image(image_path: str):
    model = load_clip_model()

    image = Image.open(image_path)

    result = model(
        image,
        candidate_labels=LABELS,
    )

    top_result = result[0]

    CONFIDENCE_THRESHOLD = 0.60

    defect_detected = (
        top_result["label"] != "a product in perfect condition"
        and top_result["score"] >= CONFIDENCE_THRESHOLD
    )

    return {
        "label": top_result["label"],
        "confidence": round(top_result["score"], 2),
        "defect_detected": defect_detected,
    }