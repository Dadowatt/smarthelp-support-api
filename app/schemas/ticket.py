from pydantic import BaseModel


class VisionResult(BaseModel):
    label: str
    confidence: float
    defect_detected: bool


class DiagnosticResult(BaseModel):
    resume: str | None = None
    statut_final: str | None = None
    action_recommandee: str | None = None


class RagResult(BaseModel):
    policy: str
    confidence: float
    policy_status: str | None = None
    diagnostic: DiagnosticResult | None = None


class TicketResponse(BaseModel):
    message: str
    description: str | None = None
    transcription: str | None = None
    vision_result: VisionResult | None = None
    rag_result: RagResult | None = None
    audio_received: bool
    image_received: bool