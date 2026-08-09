from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from app.schemas.ticket import TicketResponse
from app.services.audio.service import process_audio
from app.services.vision.service import process_image

from app.utils.file_validator import (
    validate_audio_file,
    validate_audio_size,
    validate_image_file,
    validate_image_size,
)

from app.services.rag.service import search_policy

router = APIRouter(tags=["Support"])

@router.post("/support-ticket", response_model=TicketResponse)
async def create_support_ticket(
    description: str | None = Form(default=None),
    audio: UploadFile | None = File(default=None),
    image: UploadFile | None = File(default=None),
):

    if description:
        description = description.strip()

    if description and description.lower() == "string":
        description = None

    if not audio and not image and not description:
        raise HTTPException(
            status_code=400,
            detail=(
                "Vous devez fournir au moins un audio, une image ou une description."
            ),
        )

    transcription = None
    vision_result = None

    # =========================
    #  ANALYSE AUDIO
    # =========================

    if audio:
        await validate_audio_size(audio)
        validate_audio_file(audio)

        transcription = await process_audio(audio)

    # =========================
    #  ANALYSE IMAGE
    # =========================

    if image:
        await validate_image_size(image)
        validate_image_file(image)

        vision_result = await process_image(image)

    # =========================
    #  VERIFICATION IMAGE
    # =========================

    image_relevant = (
        vision_result is not None
        and vision_result.get("image_relevant", False)
    )

    if image and not image_relevant and not description and not transcription:
        # =========================
        #  VERIFICATION COHERENCE
        # =========================

        client_text = ""

        if description:
            client_text += " " + description.lower()

        if transcription:
            client_text += " " + transcription.lower()

        damage_words = [
            "cassé",
            "casse",
            "fissuré",
            "fissure",
            "endommagé",
            "endommage",
            "brisé",
            "brisée",
            "défectueux",
            "defectueux",
        ]

        client_reports_damage = any(
            word in client_text
            for word in damage_words
        )

        if (
            image_relevant
            and vision_result is not None
            and client_reports_damage
            and not vision_result.get("defect_detected", False)
        ):
            return TicketResponse(
                message="Ticket reçu avec succès.",
                description=description,
                transcription=transcription,
                vision_result=vision_result,
                rag_result={
                    "policy": None,
                    "rule": None,
                    "confidence": 0.0,
                    "policy_status": "À vérifier",
                    "missing_information": [
                        "La description indique un dommage, mais aucun dommage clair n'est détecté sur la photo."
                    ],
                },
                audio_received=audio is not None,
                image_received=image_relevant,
            )
        raise HTTPException(
            status_code=400,
            detail=(
                "La photo ne permet pas de vérifier le problème signalé. "
                "Veuillez envoyer une photo claire du produit concerné "
                "et du dommage constaté."
            ),
        )

    # =========================
    #  CONSTRUCTION QUERY RAG
    # =========================

    query_parts = []

    if description:
        query_parts.append(
            f"Description client : {description}"
        )

    if transcription:
        query_parts.append(
            f"Message vocal client : {transcription}"
        )

    if image_relevant:
        visual_query = f"""
    Analyse visuelle :
    Label : {vision_result["label"]}

    Défaut détecté :
    {vision_result["defect_detected"]}
    """
        if vision_result.get("defect_detected", False):
            visual_query += """
    La photo montre un dommage visible sur le produit.
    Le produit est cassé, endommagé ou fissuré.
    Il s'agit d'une preuve visuelle de dommage.
    """

        query_parts.append(visual_query)

    query = "\n".join(query_parts)

    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Impossible d'analyser la demande client.",
        )

    # =========================
    #  RECHERCHE RAG
    # =========================

    rag_result = await search_policy(
        query,
        image_received=image_relevant,
        audio_received=audio is not None,
    )

    # =====================================
    #  VERIFICATION COHERENCE TEXTE / IMAGE
    # =========================================

    if image_relevant and vision_result:
        text_for_check = " ".join(
            part for part in [description, transcription]
            if part
        ).lower()

        damage_keywords = [
            "cassé",
            "cassée",
            "casse",
            "endommagé",
            "endommagée",
            "fissuré",
            "fissurée",
            "fissure",
        ]

        text_reports_damage = any(
            keyword in text_for_check
            for keyword in damage_keywords
        )

        image_shows_no_damage = (
            vision_result.get("defect_detected") is False
        )

        if text_reports_damage and image_shows_no_damage:
            rag_result["policy_status"] = "À vérifier"
            rag_result["missing_information"] = [
                "La photo fournie ne permet pas de confirmer le dommage signalé. "
                "Veuillez envoyer une photo claire du produit montrant le défaut constaté."
            ]

    return TicketResponse(
        message="Ticket reçu avec succès.",
        description=description,
        transcription=transcription,
        vision_result=vision_result,
        rag_result=rag_result,
        audio_received=audio is not None,
        image_received=image_relevant,
    )