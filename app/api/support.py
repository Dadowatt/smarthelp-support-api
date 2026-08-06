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


@router.post(
    "/support-ticket",
    response_model=TicketResponse
)
async def create_support_ticket(
    description: str | None = Form(default=None),
    audio: UploadFile | None = File(default=None),
    image: UploadFile | None = File(default=None),
):

    if description:
        description = description.strip()


    if not audio and not image and not description:
        raise HTTPException(
            status_code=400,
            detail=(
                "Vous devez fournir au moins "
                "un audio, une image ou une description."
            )
        )


    transcription = None
    vision_result = None


    # =========================
    # 1 - ANALYSE AUDIO
    # =========================

    if audio:

        await validate_audio_size(audio)
        validate_audio_file(audio)

        transcription = await process_audio(audio)



    # =========================
    # 2 - ANALYSE IMAGE
    # =========================

    if image:

        await validate_image_size(image)
        validate_image_file(image)

        vision_result = await process_image(image)



    # =========================
    # 3 - CONSTRUCTION QUERY RAG
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


    if vision_result:

        query_parts.append(
            f"""
Analyse visuelle :
Label : {vision_result["label"]}

Défaut détecté :
{vision_result["defect_detected"]}
"""
        )


    query = "\n".join(query_parts)
    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Impossible d'analyser la demande client."
        )

    rag_result = await search_policy(query)



    return TicketResponse(
        message="Ticket reçu avec succès.",
        description=description,
        transcription=transcription,
        vision_result=vision_result,
        rag_result=rag_result,
        audio_received=audio is not None,
        image_received=image is not None,
    )