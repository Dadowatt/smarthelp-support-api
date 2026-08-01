from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.ticket import TicketResponse
from app.services.audio.service import process_audio
from app.services.vision.service import process_image

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

    if audio is not None:
        await validate_audio_size(audio)
        validate_audio_file(audio)
        transcription = await process_audio(audio)

    if image is not None:
        await validate_image_size(image)
        validate_image_file(image)
        vision_result = await process_image(image)

    return TicketResponse(
        message="Ticket reçu avec succès.",
        description=description,
        transcription=transcription,
        vision_result=vision_result,
        audio_received=audio is not None,
        image_received=image is not None,
    )