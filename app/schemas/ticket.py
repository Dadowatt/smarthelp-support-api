from pydantic import BaseModel


class TicketResponse(BaseModel):
    message: str
    description: str | None = None
    transcription: str | None = None
    audio_received: bool
    image_received: bool