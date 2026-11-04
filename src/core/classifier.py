from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from config.settings import (
    MAX_FEATURES,
    NGRAM_RANGE,
    RANDOM_STATE,
    RISK_HIGH,
    RISK_LOW,
    DECISION_THRESHOLD,
    ACTIVE_MODEL_FILE,
    VECTORIZER_FILE,
)


@dataclass
class PredictionResult:
    label: str          # "phishing" | "seguro"
    risk_level: str     # "alto" | "medio" | "bajo"
    confidence: float   # 0.0 – 1.0  (probability of phishing)
    probabilities: dict[str, float]


def _risk_level(phishing_prob: float) -> str:
    if phishing_prob >= RISK_HIGH:
        return "alto"
    if phishing_prob >= RISK_LOW:
        return "medio"
    return "bajo"


def build_rf_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=MAX_FEATURES,
            ngram_range=NGRAM_RANGE,
            sublinear_tf=True,
        )),
        ("clf", RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )),
    ])


def build_svm_pipeline() -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=MAX_FEATURES,
            ngram_range=NGRAM_RANGE,
            sublinear_tf=True,
        )),
        ("clf", LinearSVC(
            C=1.0,
            max_iter=2000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        )),
    ])


def save_model(pipeline: Pipeline, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, path)


def load_model(path: Path) -> Pipeline:
    if not path.exists():
        raise FileNotFoundError(
            f"Modelo no encontrado en {path}. "
            "Ejecuta scripts/train_model.py primero."
        )
    return joblib.load(path)


class PhishingClassifier:
    def __init__(self, model_path: Path = ACTIVE_MODEL_FILE) -> None:
        self._pipeline: Pipeline = load_model(model_path)
        self._has_proba = hasattr(self._pipeline.named_steps["clf"], "predict_proba")

    def predict(self, text: str) -> PredictionResult:
        if self._has_proba:
            proba = self._pipeline.predict_proba([text])[0]
            classes = self._pipeline.classes_
            prob_map = dict(zip(classes.tolist(), proba.tolist()))
            phishing_prob = float(prob_map.get(1, prob_map.get("1", 0.0)))
        else:
            # LinearSVC uses decision_function — convert to pseudo-probability
            decision = self._pipeline.decision_function([text])[0]
            phishing_prob = float(1 / (1 + np.exp(-decision)))
            prob_map = {"0": round(1 - phishing_prob, 4), "1": round(phishing_prob, 4)}

        label = "phishing" if phishing_prob >= DECISION_THRESHOLD else "seguro"
        return PredictionResult(
            label=label,
            risk_level=_risk_level(phishing_prob) if label == "phishing" else "bajo",
            confidence=round(phishing_prob, 4),
            probabilities=prob_map,
        )

    def get_vectorizer(self) -> TfidfVectorizer:
        return self._pipeline.named_steps["tfidf"]

    def get_feature_names(self) -> list[str]:
        return self.get_vectorizer().get_feature_names_out().tolist()
