from pydantic import BaseModel


class VisionResult(BaseModel):
    label: str
    confidence: float
    defect_detected: bool


class RagResult(BaseModel):
    policy: str
    confidence: float
    status: str | None = None


class TicketResponse(BaseModel):
    message: str
    description: str | None = None
    transcription: str | None = None
    vision_result: VisionResult | None = None
    rag_result: RagResult | None = None
    audio_received: bool
    image_received: bool