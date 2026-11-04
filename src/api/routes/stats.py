from __future__ import annotations

from fastapi import APIRouter
from src.data.history import get_stats

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/")
def stats() -> dict:
    return get_stats()
