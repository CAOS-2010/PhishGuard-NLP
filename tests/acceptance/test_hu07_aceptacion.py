"""
Pruebas de aceptacion — HU-07: Integracion del motor de deteccion
=================================================================
Criterio oficial:
    "POST /analyze/ responde en menos de tres segundos con JSON completo
     y persiste cada analisis en SQLite."

Cobertura:
    CA-07-01  El endpoint responde HTTP 200
    CA-07-02  El JSON incluye todos los campos requeridos
    CA-07-03  El campo response_time_ms esta presente y es numerico
    CA-07-04  response_time_ms < 3000 ms (criterio de aceptacion)
    CA-07-05  label toma valores validos
    CA-07-06  risk_level toma valores validos
    CA-07-07  confidence esta en rango [0, 1]
    CA-07-08  explainability contiene los cuatro subcampos requeridos
    CA-07-09  urls_found es una lista
    CA-07-10  Cada analisis se persiste en SQLite (GET /history/ lo confirma)
    CA-07-11  El registro persistido incluye urls_found
    CA-07-12  El registro persistido incluye domain_mismatch
    CA-07-13  El registro persistido incluye response_time_ms
    CA-07-14  Correo de phishing en ingles clasificado correctamente
    CA-07-15  Correo de phishing en espanol clasificado correctamente
               (prueba de la capa de traduccion)
    CA-07-16  Correo seguro no clasificado como phishing
    CA-07-17  El endpoint rechaza texto menor a 10 caracteres (HTTP 422)
    CA-07-18  Cinco llamadas consecutivas cumplen el criterio de 3 s
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.api.main import app

client = TestClient(app)

# ── Muestras de prueba ────────────────────────────────────────────────────────

PHISHING_EN = {
    "sender": "security@bank-alert-verify.com",
    "subject": "URGENT: Your account has been suspended",
    "text": (
        "Dear Customer, your account has been suspended due to suspicious activity. "
        "Please verify your information immediately at "
        "http://secure-bank-login.verify-now.com "
        "or your access will be permanently blocked within 24 hours. "
        "Confirm your username, password and PIN to restore access."
    ),
}

PHISHING_ES = {
    "sender": "seguridad@banco-bogota-verificacion.com",
    "subject": "URGENTE: Su cuenta ha sido bloqueada",
    "text": (
        "Su cuenta bancaria ha sido SUSPENDIDA por actividad sospechosa. "
        "Para evitar el bloqueo definitivo verifique sus datos INMEDIATAMENTE en "
        "http://banco-bogota-seguro.verificar-cuenta.net/login "
        "Ingrese su cedula, clave y pin. "
        "Si no confirma en 24 horas su cuenta sera CANCELADA."
    ),
}

SAFE_ES = {
    "sender": "extractos@davivienda.com.co",
    "subject": "Tu extracto de agosto esta disponible",
    "text": (
        "Hola, tu extracto de agosto esta disponible en la sucursal virtual. "
        "Saldo final: 3.990.000 COP. "
        "Para consultarlo ingresa con tus datos habituales. "
        "Davivienda. Entidad vigilada por la Superfinanciera."
    ),
}


# ── CA-07-01 a CA-07-03: respuesta basica ────────────────────────────────────

class TestRespuestaBasica:

    def test_ca0701_endpoint_responde_200(self):
        """CA-07-01: POST /analyze/ devuelve HTTP 200."""
        r = client.post("/analyze/", json=PHISHING_EN)
        assert r.status_code == 200

    def test_ca0702_json_contiene_todos_los_campos(self):
        """CA-07-02: La respuesta incluye todos los campos del contrato JSON."""
        data = client.post("/analyze/", json=PHISHING_EN).json()
        campos_requeridos = [
            "label", "risk_level", "confidence", "probabilities",
            "explainability", "urls_found", "domain_mismatch", "response_time_ms",
        ]
        for campo in campos_requeridos:
            assert campo in data, f"Falta el campo '{campo}' en la respuesta"

    def test_ca0703_response_time_ms_es_numerico(self):
        """CA-07-03: response_time_ms esta presente y es un numero positivo."""
        data = client.post("/analyze/", json=PHISHING_EN).json()
        assert isinstance(data["response_time_ms"], (int, float))
        assert data["response_time_ms"] > 0


# ── CA-07-04: criterio de tiempo < 3 s ───────────────────────────────────────

class TestTiempoRespuesta:

    def test_ca0704_responde_en_menos_de_3_segundos(self):
        """CA-07-04: response_time_ms < 3000 ms (criterio de aceptacion de HU-07)."""
        data = client.post("/analyze/", json=PHISHING_ES).json()
        assert data["response_time_ms"] < 3000, (
            f"La respuesta tardo {data['response_time_ms']:.0f} ms, "
            f"supera el limite de 3000 ms."
        )

    def test_ca0718_cinco_llamadas_consecutivas_bajo_3s(self):
        """CA-07-18: Cinco llamadas consecutivas (texto en ingles, sin traduccion)
        cumplen el criterio de 3 s excluyendo latencia de red externa."""
        safe_en = {
            "text": (
                "Hi, this is a reminder that your monthly bank statement is ready. "
                "Your account balance is positive. No action required. "
                "Please log in to your online banking to view the full statement."
            )
        }
        tiempos = []
        for _ in range(5):
            data = client.post("/analyze/", json=safe_en).json()
            tiempos.append(data["response_time_ms"])

        excedidos = [t for t in tiempos if t >= 3000]
        assert not excedidos, (
            f"Las siguientes llamadas excedieron 3000 ms: {excedidos}"
        )


# ── CA-07-05 a CA-07-09: validez de los campos del JSON ──────────────────────

class TestEstructuraJSON:

    def test_ca0705_label_valores_validos(self):
        """CA-07-05: label solo puede ser 'phishing' o 'seguro'."""
        data = client.post("/analyze/", json=PHISHING_EN).json()
        assert data["label"] in ("phishing", "seguro")

    def test_ca0706_risk_level_valores_validos(self):
        """CA-07-06: risk_level solo puede ser 'alto', 'medio' o 'bajo'."""
        data = client.post("/analyze/", json=PHISHING_EN).json()
        assert data["risk_level"] in ("alto", "medio", "bajo")

    def test_ca0707_confidence_en_rango(self):
        """CA-07-07: confidence esta en el rango [0.0, 1.0]."""
        data = client.post("/analyze/", json=PHISHING_EN).json()
        assert 0.0 <= data["confidence"] <= 1.0

    def test_ca0708_explainability_contiene_subcampos(self):
        """CA-07-08: explainability tiene los cuatro subcampos requeridos."""
        xai = client.post("/analyze/", json=PHISHING_EN).json()["explainability"]
        for campo in ["top_phishing_features", "urgency_keywords_found",
                      "social_engineering_score", "summary"]:
            assert campo in xai, f"Falta '{campo}' en explainability"

    def test_ca0709_urls_found_es_lista(self):
        """CA-07-09: urls_found es siempre una lista (puede estar vacia)."""
        data = client.post("/analyze/", json=SAFE_ES).json()
        assert isinstance(data["urls_found"], list)


# ── CA-07-10 a CA-07-13: persistencia en SQLite ──────────────────────────────

class TestPersistenciaSQLite:

    def test_ca0710_analisis_persiste_en_historial(self):
        """CA-07-10: Cada POST /analyze/ genera un registro en GET /history/."""
        antes = client.get("/history/").json()["total"]
        client.post("/analyze/", json=PHISHING_EN)
        despues = client.get("/history/").json()["total"]
        assert despues == antes + 1, (
            "El historial no incremento despues del analisis"
        )

    def test_ca0711_historial_incluye_urls_found(self):
        """CA-07-11: El registro persistido incluye el campo urls_found."""
        client.post("/analyze/", json=PHISHING_ES)
        rec = client.get("/history/?limit=1").json()["records"][0]
        assert "urls_found" in rec

    def test_ca0712_historial_incluye_domain_mismatch(self):
        """CA-07-12: El registro persistido incluye el campo domain_mismatch."""
        client.post("/analyze/", json=PHISHING_ES)
        rec = client.get("/history/?limit=1").json()["records"][0]
        assert "domain_mismatch" in rec

    def test_ca0713_historial_incluye_response_time_ms(self):
        """CA-07-13: El registro persistido incluye response_time_ms."""
        client.post("/analyze/", json=PHISHING_EN)
        rec = client.get("/history/?limit=1").json()["records"][0]
        assert "response_time_ms" in rec
        assert rec["response_time_ms"] is not None
        assert rec["response_time_ms"] > 0

    def test_ca0711_urls_found_persiste_correctamente(self):
        """CA-07-11b: Las URLs del correo se guardan en el historial."""
        client.post("/analyze/", json=PHISHING_ES)
        rec = client.get("/history/?limit=1").json()["records"][0]
        urls_raw = rec["urls_found"]
        urls = json.loads(urls_raw) if isinstance(urls_raw, str) else urls_raw
        assert isinstance(urls, list)
        assert any("banco-bogota" in u for u in urls), (
            f"La URL del phishing no fue persistida. urls_found={urls}"
        )


# ── CA-07-14 a CA-07-16: clasificacion correcta ──────────────────────────────

class TestClasificacionCorrecta:

    def test_ca0714_phishing_en_ingles_detectado(self):
        """CA-07-14: Correo de phishing en ingles clasificado como phishing."""
        data = client.post("/analyze/", json=PHISHING_EN).json()
        assert data["label"] == "phishing", (
            f"Phishing EN clasificado como '{data['label']}' "
            f"(confianza: {data['confidence']:.2%})"
        )

    def test_ca0715_phishing_en_espanol_detectado(self):
        """CA-07-15: Correo de phishing en espanol detectado via traduccion + hybrid scoring."""
        data = client.post("/analyze/", json=PHISHING_ES).json()
        assert data["label"] == "phishing", (
            f"Phishing ES clasificado como '{data['label']}' "
            f"(confianza: {data['confidence']:.2%}). "
            f"Verificar capa de traduccion y hybrid scoring."
        )

    def test_ca0716_correo_seguro_no_es_phishing(self):
        """CA-07-16: Extracto bancario legitimo NO clasificado como phishing."""
        data = client.post("/analyze/", json=SAFE_ES).json()
        assert data["label"] == "seguro", (
            f"Correo seguro clasificado como '{data['label']}' "
            f"(confianza: {data['confidence']:.2%}). Falso positivo."
        )


# ── CA-07-17: validacion de entrada ──────────────────────────────────────────

class TestValidacionEntrada:

    def test_ca0717_texto_corto_rechazado_con_422(self):
        """CA-07-17: Texto menor a 10 caracteres devuelve HTTP 422."""
        r = client.post("/analyze/", json={"text": "corto"})
        assert r.status_code == 422
