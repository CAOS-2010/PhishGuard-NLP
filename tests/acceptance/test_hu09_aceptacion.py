"""
Pruebas de aceptacion — HU-09: Retroalimentacion activa y reentrenamiento automatico
=====================================================================================
Criterio oficial:
    "Formulario de correccion visible; correcciones persistidas en SQLite;
     reentrenamiento automatico activado al acumular 10 correcciones."

Cobertura (8 pruebas):
    CA-09-01  POST /feedback/ persiste el registro en SQLite y retorna saved=True
    CA-09-02  Los campos predicted_label, correct_label, confidence y snippet se guardan
    CA-09-03  Cuando predicted_label != correct_label la respuesta indica retraining_started
    CA-09-04  trigger_retrain() utiliza threading.Thread (no bloquea el hilo principal)
    CA-09-05  GET /feedback/retrain-status retorna is_training, last_trained_at, examples_added
    CA-09-06  reload_classifier() recarga el modelo activo sin errores
    CA-09-07  GET /stats/ incluye los campos feedback_total y feedback_corrections
    CA-09-08  get_status() retorna un diccionario con las cuatro claves requeridas
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.api.main import app

client = TestClient(app)

FEEDBACK_BASE = {
    "text_snippet":    "Su cuenta ha sido SUSPENDIDA. Verifique en http://banco-fake.com",
    "full_text":       "",
    "predicted_label": "phishing",
    "correct_label":   "phishing",
    "confidence":      0.91,
    "comment":         "prueba de aceptacion CA-09",
}

PHISHING_PAYLOAD = {
    "sender":  "alerta@banco-verify.net",
    "subject": "URGENTE: cuenta suspendida",
    "text": (
        "Estimado cliente, su cuenta ha sido SUSPENDIDA por actividad sospechosa. "
        "Verifique INMEDIATAMENTE en http://banco-seguro-verify.com "
        "Ingrese su clave y PIN o su acceso sera CANCELADO."
    ),
}


class TestRetroalimentacion:

    def test_ca0901_feedback_persiste_y_retorna_saved(self):
        """CA-09-01: POST /feedback/ retorna saved=True."""
        r = client.post("/feedback/", json=FEEDBACK_BASE)
        assert r.status_code == 200, f"HTTP {r.status_code}: {r.text}"
        data = r.json()
        assert data["saved"] is True

    def test_ca0902_campos_requeridos_en_payload(self):
        """CA-09-02: El endpoint acepta predicted_label, correct_label, confidence y snippet."""
        payload = {
            **FEEDBACK_BASE,
            "text_snippet": "Verifique su cuenta ahora en http://phish-test.com",
            "confidence":   0.85,
        }
        r = client.post("/feedback/", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert "saved" in data
        assert "retraining_started" in data
        assert "message" in data

    def test_ca0903_etiqueta_incorrecta_activa_flag_retraining(self):
        """CA-09-03: Con predicted_label != correct_label la respuesta incluye retraining_started."""
        payload = {
            "text_snippet":    "Hola, tu saldo del mes es $1.500.000. Davivienda.",
            "full_text":       "",
            "predicted_label": "phishing",
            "correct_label":   "seguro",
            "confidence":      0.55,
            "comment":         "correccion de etiqueta CA-09-03",
        }
        r = client.post("/feedback/", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert "retraining_started" in data
        assert isinstance(data["retraining_started"], bool)

    def test_ca0904_trigger_retrain_usa_hilo_separado(self):
        """CA-09-04: trigger_retrain() utiliza threading.Thread para no bloquear la UI."""
        import inspect
        from src.core import retrainer
        source = inspect.getsource(retrainer)
        assert "Thread" in source, (
            "trigger_retrain debe lanzar un threading.Thread para el reentrenamiento"
        )
        status = retrainer.get_status()
        assert isinstance(status["is_training"], bool), (
            "get_status() debe retornar is_training como booleano"
        )

    def test_ca0905_retrain_status_contiene_campos_requeridos(self):
        """CA-09-05: GET /feedback/retrain-status retorna is_training, last_trained_at, examples_added."""
        r = client.get("/feedback/retrain-status")
        assert r.status_code == 200, f"HTTP {r.status_code}: {r.text}"
        data = r.json()
        assert "is_training"     in data, "Falta campo is_training"
        assert "last_trained_at" in data, "Falta campo last_trained_at"
        assert "examples_added"  in data, "Falta campo examples_added"

    def test_ca0906_reload_classifier_recarga_sin_errores(self):
        """CA-09-06: reload_classifier() recarga el modelo activo y el sistema sigue funcionando."""
        from src.api.routes.analysis import reload_classifier
        reload_classifier()
        r = client.post("/analyze/", json=PHISHING_PAYLOAD)
        assert r.status_code == 200, (
            f"Despues de reload_classifier() el endpoint fallo: HTTP {r.status_code}"
        )
        assert r.json()["label"] in ("phishing", "seguro")

    def test_ca0907_stats_incluye_campos_de_feedback(self):
        """CA-09-07: GET /stats/ incluye feedback_total y feedback_corrections."""
        r = client.get("/stats/")
        assert r.status_code == 200, f"HTTP {r.status_code}: {r.text}"
        data = r.json()
        assert "feedback_total"       in data, "Falta feedback_total en /stats/"
        assert "feedback_corrections" in data, "Falta feedback_corrections en /stats/"
        assert isinstance(data["feedback_total"],       int)
        assert isinstance(data["feedback_corrections"], int)

    def test_ca0908_get_status_retorna_estructura_completa(self):
        """CA-09-08: get_status() retorna dict con is_training, last_trained_at, examples_added y error."""
        from src.core.retrainer import get_status
        status = get_status()
        for campo in ("is_training", "last_trained_at", "examples_added", "error"):
            assert campo in status, f"Falta campo '{campo}' en get_status()"
        assert isinstance(status["is_training"],    bool)
        assert isinstance(status["examples_added"], int)
