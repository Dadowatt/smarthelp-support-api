from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.ticket import TicketResponse, RagResult
from app.services.audio.service import process_audio
from app.services.vision.service import process_image
from app.services.rag.service import search_policy

from app.utils.file_validator import (
    validate_audio_file,
    validate_audio_size,
    validate_image_file,
    validate_image_size,
)

router = APIRouter(tags=["Support"])


@router.post("/support-ticket", response_model=TicketResponse)
async def create_support_ticket(
    description: str | None = Form(default=None),
    audio: UploadFile | None = File(default=None),
    image: UploadFile | None = File(default=None),
):
    transcription = None
    vision_result = None
    rag_result = None

    # ==========================
    # Traitement audio
    # ==========================
    if audio is not None:
        await validate_audio_size(audio)
        validate_audio_file(audio)
        transcription = await process_audio(audio)

    # ==========================
    # Traitement image
    # ==========================
    if image is not None:
        await validate_image_size(image)
        validate_image_file(image)
        vision_result = await process_image(image)

    # ==========================
    # Construction du contexte
    # ==========================
    context = []

    if description:
        context.append(description)

    if transcription:
        context.append(transcription)

    if (
        vision_result is not None
        and vision_result.defect_detected
    ):
        context.append(
            f"Analyse image : {vision_result.label}"
        )

    combined_text = " ".join(context)

    # ==========================
    # Recherche RAG
    # ==========================
    if combined_text:
        rag = search_policy(combined_text)

        rag_result = RagResult(
            policy=rag["policy"],
            status=rag["status"],
            confidence=rag["confidence"],
        )

    return TicketResponse(
        message="Ticket analysé avec succès.",
        description=description,
        transcription=transcription,
        vision_result=vision_result,
        rag_result=rag_result,
        audio_received=audio is not None,
        image_received=image is not None,
    )