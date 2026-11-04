"""
Tests de integracion para los endpoints de la API de PhishGuard NLP.
Requieren que el modelo este entrenado (models/active_model.joblib debe existir).
Se ejecutan contra la app en memoria con TestClient de FastAPI (sin servidor externo).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)

PHISHING_PAYLOAD = {
    "sender": "security@bank-alert-verify.com",
    "subject": "URGENT: Your account has been suspended - verify now",
    "text": (
        "Dear Customer, your account has been suspended due to suspicious activity. "
        "Please verify your information immediately at http://secure-bank-login.verify-now.com "
        "or your access will be permanently blocked within 24 hours. "
        "Confirm your username, password and PIN to restore access."
    ),
}
PHISHING_SAMPLE = PHISHING_PAYLOAD["text"]

SAFE_SAMPLE = (
    "Hi team, just a reminder that our weekly meeting is scheduled for Thursday at 3pm. "
    "Please review the attached agenda and let me know if you have any topics to add. "
    "Looking forward to seeing everyone there. Best regards, Maria."
)


# ── /health ───────────────────────────────────────────────────────────────────

class TestHealth:
    def test_health_returns_ok(self):
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_schema(self):
        data = client.get("/health").json()
        assert "status" in data
        assert "model_loaded" in data
        assert data["status"] == "ok"

    def test_health_model_loaded(self):
        data = client.get("/health").json()
        assert data["model_loaded"] is True, (
            "El modelo no esta cargado. Ejecuta scripts/train_model.py primero."
        )


# ── /analyze/ ─────────────────────────────────────────────────────────────────

class TestAnalyze:
    def test_analyze_phishing_returns_200(self):
        r = client.post("/analyze/", json={"text": PHISHING_SAMPLE})
        assert r.status_code == 200

    def test_analyze_safe_returns_200(self):
        r = client.post("/analyze/", json={"text": SAFE_SAMPLE})
        assert r.status_code == 200

    def test_analyze_response_schema(self):
        data = client.post("/analyze/", json={"text": PHISHING_SAMPLE}).json()
        assert "label" in data
        assert "risk_level" in data
        assert "confidence" in data
        assert "probabilities" in data
        assert "explainability" in data
        assert "urls_found" in data
        assert "domain_mismatch" in data

    def test_analyze_label_is_valid(self):
        data = client.post("/analyze/", json={"text": PHISHING_SAMPLE}).json()
        assert data["label"] in ("phishing", "seguro")

    def test_analyze_risk_level_is_valid(self):
        data = client.post("/analyze/", json={"text": PHISHING_SAMPLE}).json()
        assert data["risk_level"] in ("alto", "medio", "bajo")

    def test_analyze_confidence_range(self):
        data = client.post("/analyze/", json={"text": PHISHING_SAMPLE}).json()
        assert 0.0 <= data["confidence"] <= 1.0

    def test_analyze_explainability_schema(self):
        data = client.post("/analyze/", json={"text": PHISHING_SAMPLE}).json()
        xai = data["explainability"]
        assert "top_phishing_features" in xai
        assert "urgency_keywords_found" in xai
        assert "social_engineering_score" in xai
        assert "summary" in xai

    def test_analyze_detects_urls(self):
        text = "Haga clic en https://banco-falso.com para verificar."
        data = client.post("/analyze/", json={"text": text}).json()
        assert len(data["urls_found"]) > 0

    def test_analyze_with_subject_and_sender(self):
        r = client.post("/analyze/", json={
            "text": PHISHING_SAMPLE,
            "subject": "Alerta: cuenta bloqueada",
            "sender": "soporte@banco-falso.xyz",
        })
        assert r.status_code == 200

    def test_analyze_rejects_short_text(self):
        r = client.post("/analyze/", json={"text": "corto"})
        assert r.status_code == 422

    def test_analyze_phishing_sample_classified_correctly(self):
        data = client.post("/analyze/", json=PHISHING_PAYLOAD).json()
        assert data["label"] == "phishing", (
            f"El correo de phishing fue clasificado como '{data['label']}'. "
            f"Confianza: {data['confidence']:.2%}"
        )

    def test_analyze_safe_sample_classified_correctly(self):
        data = client.post("/analyze/", json={"text": SAFE_SAMPLE}).json()
        assert data["label"] == "seguro", (
            f"El correo seguro fue clasificado como '{data['label']}'. "
            f"Confianza: {data['confidence']:.2%}"
        )

    def test_analyze_urgency_keywords_detected(self):
        # Uses Spanish urgency keywords that match URGENCY_KEYWORDS in settings.py
        es_phishing = (
            "Estimado cliente, su cuenta bancaria ha sido suspendida de forma urgente. "
            "Debe ingresar sus datos bancarios inmediatamente para evitar el bloqueo "
            "definitivo. Haga clic en el enlace para restaurar el acceso."
        )
        data = client.post("/analyze/", json={"text": es_phishing}).json()
        kws = data["explainability"]["urgency_keywords_found"]
        assert len(kws) > 0, "Se esperaban palabras de urgencia en el correo de phishing en espanol."


# ── /history/ ─────────────────────────────────────────────────────────────────

class TestHistory:
    def test_history_returns_200(self):
        r = client.get("/history/")
        assert r.status_code == 200

    def test_history_schema(self):
        data = client.get("/history/").json()
        assert "total" in data
        assert "records" in data
        assert isinstance(data["records"], list)

    def test_history_records_populated_after_analyze(self):
        client.post("/analyze/", json={"text": PHISHING_SAMPLE})
        data = client.get("/history/").json()
        assert data["total"] >= 1

    def test_history_record_schema(self):
        client.post("/analyze/", json={"text": PHISHING_SAMPLE})
        records = client.get("/history/").json()["records"]
        assert len(records) > 0
        r = records[0]
        assert "id" in r
        assert "analyzed_at" in r
        assert "label" in r
        assert "risk_level" in r
        assert "confidence" in r

    def test_history_limit_param(self):
        for _ in range(3):
            client.post("/analyze/", json={"text": PHISHING_SAMPLE})
        data = client.get("/history/", params={"limit": 2}).json()
        assert len(data["records"]) <= 2

    def test_history_delete_returns_200(self):
        r = client.delete("/history/")
        assert r.status_code == 200

    def test_history_delete_clears_records(self):
        client.post("/analyze/", json={"text": PHISHING_SAMPLE})
        client.delete("/history/")
        data = client.get("/history/").json()
        assert data["total"] == 0

    def test_history_delete_schema(self):
        data = client.delete("/history/").json()
        assert "deleted" in data
        assert data["deleted"] is True
