from pydantic import BaseModel


class VisionResult(BaseModel):
    label: str
    confidence: float
    defect_detected: bool


class TicketResponse(BaseModel):
    message: str
    description: str | None = None
    transcription: str | None = None
    vision_result: VisionResult | None = None
    audio_received: bool
    image_received: bool