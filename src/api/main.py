from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import API_HOST, API_PORT
from src.api.routes.analysis import router as analysis_router
from src.api.routes.feedback import router as feedback_router
from src.api.routes.history import router as history_router
from src.api.routes.stats import router as stats_router
from src.api.schemas import HealthResponse
from src.data.history import init_db


def _ensure_nltk():
    import nltk
    for corpus in ("stopwords", "punkt", "punkt_tab"):
        try:
            nltk.download(corpus, quiet=True)
        except Exception:
            pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_nltk()
    init_db()
    yield


app = FastAPI(
    title="PhishGuard NLP",
    description="API para detección de phishing bancario mediante NLP y aprendizaje supervisado.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analysis_router)
app.include_router(history_router)
app.include_router(feedback_router)
app.include_router(stats_router)


@app.get("/health", response_model=HealthResponse, tags=["System"])
def health() -> HealthResponse:
    from config.settings import ACTIVE_MODEL_FILE
    return HealthResponse(
        status="ok",
        model_loaded=ACTIVE_MODEL_FILE.exists(),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host=API_HOST, port=API_PORT, reload=True)
