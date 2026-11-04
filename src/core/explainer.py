from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from config.settings import XAI_TOP_FEATURES
from src.core.preprocessor import detect_urgency_keywords


@dataclass
class ExplainabilityReport:
    top_phishing_features: list[tuple[str, float]]   # (word, weight)
    top_safe_features: list[tuple[str, float]]
    urgency_keywords_found: list[str]
    social_engineering_score: float                  # 0.0 – 1.0
    summary: str


def explain(
    raw_text: str,
    processed_text: str,
    vectorizer: TfidfVectorizer,
    feature_importances: np.ndarray | None = None,
) -> ExplainabilityReport:
    urgency_kws = detect_urgency_keywords(raw_text)
    social_score = min(len(urgency_kws) / 10.0, 1.0)

    tfidf_matrix = vectorizer.transform([processed_text])
    feature_names = vectorizer.get_feature_names_out()

    # TF-IDF scores for this specific document
    scores = tfidf_matrix.toarray()[0]
    nonzero_idx = np.where(scores > 0)[0]
    doc_features = [(feature_names[i], float(scores[i])) for i in nonzero_idx]
    doc_features.sort(key=lambda x: x[1], reverse=True)

    if feature_importances is not None:
        # Weight by RF feature importance when available
        fi_map = {feature_names[i]: float(feature_importances[i]) for i in range(len(feature_names))}
        weighted = [(w, sc * fi_map.get(w, 0.0)) for w, sc in doc_features]
        weighted.sort(key=lambda x: x[1], reverse=True)
        top_phishing = weighted[:XAI_TOP_FEATURES]
        top_safe = weighted[-XAI_TOP_FEATURES:][::-1]
    else:
        top_phishing = doc_features[:XAI_TOP_FEATURES]
        top_safe = doc_features[-XAI_TOP_FEATURES:][::-1]

    summary = _build_summary(urgency_kws, social_score, top_phishing)

    return ExplainabilityReport(
        top_phishing_features=top_phishing,
        top_safe_features=top_safe,
        urgency_keywords_found=urgency_kws,
        social_engineering_score=round(social_score, 2),
        summary=summary,
    )


def _build_summary(
    urgency_kws: list[str],
    social_score: float,
    top_features: list[tuple[str, float]],
) -> str:
    parts: list[str] = []
    if urgency_kws:
        kw_str = ", ".join(f'"{k}"' for k in urgency_kws[:5])
        parts.append(f"Se detectaron palabras de presión psicológica: {kw_str}.")
    if social_score >= 0.5:
        parts.append("El mensaje presenta un alto nivel de ingeniería social.")
    if top_features:
        top_words = ", ".join(f'"{w}"' for w, _ in top_features[:5])
        parts.append(f"Los términos con mayor peso de riesgo son: {top_words}.")
    if not parts:
        parts.append("No se detectaron indicadores claros de phishing en el texto analizado.")
    return " ".join(parts)
