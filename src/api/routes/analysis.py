from __future__ import annotations

import concurrent.futures
import time

import numpy as np
from fastapi import APIRouter, HTTPException

from src.api.schemas import (
    AnalyzeResponse,
    AnalyzeTextRequest,
    DecisionFactors,
    ExplainabilityData,
    FeatureWeight,
    URLAnalysisData,
    URLRiskData,
)
from src.core.classifier import PhishingClassifier, _risk_level
from src.core.explainer import explain
from src.core.preprocessor import preprocess
from src.core.url_analyzer import analyze_urls
from src.data.history import save_analysis
from src.data.parser import from_text
from config.settings import RISK_LOW, DECISION_THRESHOLD

router = APIRouter(prefix="/analyze", tags=["Analysis"])

_classifier: PhishingClassifier | None = None

_TRANSLATION_TIMEOUT = 5.0  # segundos máximo para la llamada a Google Translate


def get_classifier() -> PhishingClassifier:
    global _classifier
    if _classifier is None:
        _classifier = PhishingClassifier()
    return _classifier


def reload_classifier() -> None:
    global _classifier
    _classifier = PhishingClassifier()


def _translate_to_english(text: str) -> str:
    """Detecta el idioma y traduce al inglés con timeout de 5 s."""
    try:
        from langdetect import detect
        lang = detect(text)
        if lang == "en":
            return text

        from deep_translator import GoogleTranslator
        chunks = [text[i:i + 4500] for i in range(0, len(text), 4500)]

        def _do_translate() -> str:
            return " ".join(
                GoogleTranslator(source=lang, target="en").translate(chunk)
                for chunk in chunks
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_do_translate)
            return future.result(timeout=_TRANSLATION_TIMEOUT)

    except Exception:
        pass
    return text


def _hybrid_score(
    ml_prob: float,
    social_score: float,
    url_count: int,
    urgency_count: int,
) -> float:
    """Combina la probabilidad ML con señales XAI cuando el ML es incierto."""
    xai_score = (
        0.40 * social_score
        + 0.35 * min(url_count / 2.0, 1.0)
        + 0.25 * min(urgency_count / 10.0, 1.0)
    )
    return round(0.35 * ml_prob + 0.65 * xai_score, 4)


@router.post("/", response_model=AnalyzeResponse)
def analyze_text(request: AnalyzeTextRequest) -> AnalyzeResponse:
    t_start = time.perf_counter()

    clf = get_classifier()

    parsed = from_text(request.text)
    if request.sender:
        parsed.sender = request.sender
    if request.subject:
        parsed.subject = request.subject

    full_text = f"{request.subject} {request.text}".strip()

    xai_text = full_text
    ml_text = _translate_to_english(full_text)

    processed = preprocess(ml_text)
    result = clf.predict(processed)

    vectorizer = clf.get_vectorizer()
    feature_importances: np.ndarray | None = None
    inner_clf = clf._pipeline.named_steps["clf"]
    if hasattr(inner_clf, "feature_importances_"):
        feature_importances = inner_clf.feature_importances_

    processed_xai = preprocess(xai_text)
    xai = explain(xai_text, processed_xai, vectorizer, feature_importances)

    # Análisis de URLs — usa texto completo para capturar URLs sin protocolo
    url_report = analyze_urls(full_text)
    url_count = url_report.total_urls
    urgency_count = len(xai.urgency_keywords_found)

    _HIGH_VALUE_KWS = {
        "datos bancarios", "formulario adjunto", "copia de cedula", "copia de cédula",
        "numero de cuenta", "número de cuenta", "formulario con sus datos",
    }
    raw_ml_confidence = result.confidence
    ml_uncertain = result.confidence < DECISION_THRESHOLD
    xai_strong = xai.social_engineering_score >= 0.5 and (url_count > 0 or urgency_count >= 4)
    urgency_alone = urgency_count >= 6 and xai.social_engineering_score >= 0.4
    url_high_risk = url_report.high_risk_urls > 0 and url_report.url_risk_score >= 0.45
    ml_suspicious_with_signals = result.confidence >= 0.55 and urgency_count >= 2
    data_harvesting = (
        result.confidence >= RISK_LOW
        and any(kw in _HIGH_VALUE_KWS for kw in xai.urgency_keywords_found)
        and urgency_count >= 2
    )

    hybrid_triggered = False
    data_harvesting_triggered = False

    if data_harvesting and not (xai_strong or urgency_alone or url_high_risk or ml_suspicious_with_signals):
        data_harvesting_triggered = True
        result.label = "phishing"
        result.risk_level = _risk_level(result.confidence)
        result.probabilities = {"0": round(1 - result.confidence, 4), "1": round(result.confidence, 4)}
    elif ml_uncertain and (xai_strong or urgency_alone or url_high_risk or ml_suspicious_with_signals):
        hybrid_triggered = True
        hybrid_prob = _hybrid_score(
            result.confidence, xai.social_engineering_score,
            url_count, urgency_count
        )
        if url_high_risk:
            hybrid_prob = min(hybrid_prob + url_report.url_risk_score * 0.30, 0.99)
        hybrid_prob = round(hybrid_prob, 4)
        result.confidence = hybrid_prob
        result.label = "phishing" if hybrid_prob >= RISK_LOW else "seguro"
        result.risk_level = _risk_level(hybrid_prob)
        result.probabilities = {"0": round(1 - hybrid_prob, 4), "1": round(hybrid_prob, 4)}

    response_time_ms = round((time.perf_counter() - t_start) * 1000, 2)

    save_analysis(
        sender=request.sender,
        subject=request.subject,
        label=result.label,
        risk_level=result.risk_level,
        confidence=result.confidence,
        body_snippet=request.text,
        urls_found=parsed.urls,
        domain_mismatch=parsed.domain_mismatch,
        response_time_ms=response_time_ms,
    )

    return AnalyzeResponse(
        label=result.label,
        risk_level=result.risk_level,
        confidence=result.confidence,
        probabilities=result.probabilities,
        explainability=ExplainabilityData(
            top_phishing_features=[
                FeatureWeight(word=w, weight=round(sc, 4))
                for w, sc in xai.top_phishing_features
            ],
            urgency_keywords_found=xai.urgency_keywords_found,
            social_engineering_score=xai.social_engineering_score,
            summary=xai.summary,
        ),
        url_analysis=URLAnalysisData(
            urls=[
                URLRiskData(
                    url=u.url,
                    uses_http=u.uses_http,
                    is_ip_based=u.is_ip_based,
                    is_shortener=u.is_shortener,
                    suspicious_keywords=u.suspicious_keywords,
                    brand_spoofing=u.brand_spoofing,
                    suspicious_tld=u.suspicious_tld,
                    excessive_subdomains=u.excessive_subdomains,
                    risk_score=u.risk_score,
                    risk_level=u.risk_level,
                )
                for u in url_report.urls
            ],
            total_urls=url_report.total_urls,
            high_risk_urls=url_report.high_risk_urls,
            url_risk_score=url_report.url_risk_score,
        ),
        decision_factors=DecisionFactors(
            ml_confidence=round(raw_ml_confidence, 4),
            hybrid_triggered=hybrid_triggered,
            data_harvesting_triggered=data_harvesting_triggered,
            xai_social_score=xai.social_engineering_score,
            urgency_count=urgency_count,
            url_count=url_count,
            url_risk_score=url_report.url_risk_score,
        ),
        urls_found=[u.url for u in url_report.urls],
        domain_mismatch=parsed.domain_mismatch,
        response_time_ms=response_time_ms,
    )
