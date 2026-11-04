from __future__ import annotations

from fastapi import APIRouter, Query

from src.api.schemas import ClearHistoryResponse, HistoryListResponse, HistoryRecord
from src.data.history import clear_history, count_history, get_history

router = APIRouter(prefix="/history", tags=["History"])


@router.get("/", response_model=HistoryListResponse)
def list_history(limit: int = Query(default=100, ge=1, le=500)) -> HistoryListResponse:
    records = get_history(limit=limit)
    return HistoryListResponse(
        total=count_history(),
        records=[HistoryRecord(**r) for r in records],
    )


@router.delete("/", response_model=ClearHistoryResponse)
def delete_history() -> ClearHistoryResponse:
    clear_history()
    return ClearHistoryResponse(deleted=True)
