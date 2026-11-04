from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from src.data.history import save_feedback, get_feedback
from src.core.retrainer import trigger_retrain, get_status

router = APIRouter(prefix="/feedback", tags=["Feedback"])


class FeedbackRequest(BaseModel):
    analysis_id: int | None = None
    text_snippet: str
    full_text: str = ""
    predicted_label: str
    correct_label: str
    confidence: float
    comment: str = ""


class FeedbackResponse(BaseModel):
    saved: bool
    retraining_started: bool
    message: str


@router.post("/", response_model=FeedbackResponse)
def submit_feedback(req: FeedbackRequest) -> FeedbackResponse:
    save_feedback(
        analysis_id=req.analysis_id,
        text_snippet=req.text_snippet,
        predicted_label=req.predicted_label,
        correct_label=req.correct_label,
        confidence=req.confidence,
        comment=req.comment,
    )

    retraining_started = False
    if req.predicted_label != req.correct_label and req.full_text.strip():
        from src.api.routes.analysis import reload_classifier
        retraining_started = trigger_retrain(req.full_text, req.correct_label, reload_classifier)

    msg = (
        "Corrección guardada. El modelo se está reentrenando en segundo plano (~60s)."
        if retraining_started
        else "Retroalimentacion registrada. Gracias por ayudar a mejorar el sistema."
    )
    return FeedbackResponse(saved=True, retraining_started=retraining_started, message=msg)


@router.get("/retrain-status")
def retrain_status() -> dict:
    return get_status()


@router.get("/")
def list_feedback(limit: int = 100) -> dict:
    records = get_feedback(limit)
    return {"total": len(records), "records": records}
