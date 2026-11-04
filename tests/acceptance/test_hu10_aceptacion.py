"""
Pruebas de aceptacion — HU-10: Funcionalidades avanzadas de interfaz
=====================================================================
Criterio oficial:
    "Expander 'Ver detalles del veredicto' visible; file uploader multi-archivo
     con barra de progreso; dashboard con 6 KPIs operativo."

Modulo A — Explicabilidad extendida (CA-10-01 a CA-10-08, 8 pruebas)
Modulo B — Analisis masivo por lotes y panel de estadisticas (CA-10-09 a CA-10-18, 10 pruebas)
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.api.main import app

client = TestClient(app)

PHISHING_CON_URL = {
    "sender":  "seguridad@davivienda-alert-verify.com",
    "subject": "URGENTE: Su cuenta ha sido SUSPENDIDA",
    "text": (
        "Estimado cliente, hemos detectado actividad inusual en su cuenta. "
        "Su acceso ha sido SUSPENDIDO temporalmente. "
        "Debe VERIFICAR su identidad INMEDIATAMENTE para evitar bloqueo permanente. "
        "Haga clic: http://davivienda-seguridad-verificar.com/cuenta "
        "Ingrese su cedula, clave y PIN. Tiene 24 HORAS antes del CIERRE definitivo."
    ),
}

SEGURO = {
    "sender":  "notificaciones@davivienda.com",
    "subject": "Tu extracto de cuenta - octubre 2026",
    "text": (
        "Hola, tu extracto del mes de octubre ya esta disponible. "
        "Saldo disponible: $2.450.000 COP. "
        "Puedes consultarlo en la sucursal virtual con tus datos habituales. "
        "Davivienda. Entidad vigilada por la Superfinanciera de Colombia."
    ),
}

LOTE = [
    {
        "sender": f"remitente{i}@ejemplo.com",
        "subject": f"Asunto de prueba {i}",
        "text": (
            "URGENTE verifique su cuenta en http://fake-bank.com ingrese su clave."
            if i % 2 == 0 else
            f"Hola, su extracto numero {i} esta disponible en la sucursal virtual."
        ),
    }
    for i in range(1, 4)
]


# ══════════════════════════════════════════════════════════════════════════════
# MODULO A — Explicabilidad extendida (CA-10-01 a CA-10-08)
# ══════════════════════════════════════════════════════════════════════════════

class TestExplicabilidadExtendida:

    @pytest.fixture(scope="class")
    def respuesta(self):
        r = client.post("/analyze/", json=PHISHING_CON_URL)
        assert r.status_code == 200
        return r.json()

    def test_ca1001_campo_explainability_presente(self, respuesta):
        """CA-10-01: La respuesta de /analyze/ contiene el campo explainability."""
        assert "explainability" in respuesta, (
            "El campo 'explainability' no esta en la respuesta del endpoint"
        )

    def test_ca1002_top_features_contiene_terminos(self, respuesta):
        """CA-10-02: explainability.top_phishing_features contiene al menos 1 termino."""
        features = respuesta["explainability"]["top_phishing_features"]
        assert isinstance(features, list), "top_phishing_features debe ser una lista"
        assert len(features) >= 1, (
            f"Se esperaba al menos 1 termino TF-IDF, se obtuvieron {len(features)}"
        )

    def test_ca1003_features_tienen_word_y_weight(self, respuesta):
        """CA-10-03: Cada feature tiene los campos word y weight."""
        for feat in respuesta["explainability"]["top_phishing_features"]:
            assert "word"   in feat, f"Feature sin campo 'word': {feat}"
            assert "weight" in feat, f"Feature sin campo 'weight': {feat}"
            assert isinstance(feat["weight"], (int, float))

    def test_ca1004_urgency_keywords_es_lista(self, respuesta):
        """CA-10-04: explainability.urgency_keywords_found es una lista."""
        keywords = respuesta["explainability"]["urgency_keywords_found"]
        assert isinstance(keywords, list), (
            "urgency_keywords_found debe ser una lista de cadenas"
        )

    def test_ca1005_social_score_en_rango_valido(self, respuesta):
        """CA-10-05: explainability.social_engineering_score es float en [0, 1]."""
        score = respuesta["explainability"]["social_engineering_score"]
        assert isinstance(score, (int, float)), "social_engineering_score debe ser numerico"
        assert 0.0 <= score <= 1.0, (
            f"social_engineering_score fuera de rango: {score}"
        )

    def test_ca1006_summary_tiene_contenido(self, respuesta):
        """CA-10-06: explainability.summary es una cadena con mas de 10 caracteres."""
        summary = respuesta["explainability"]["summary"]
        assert isinstance(summary, str),   "summary debe ser una cadena de texto"
        assert len(summary) > 10, (
            f"summary demasiado corto: '{summary[:50]}'"
        )

    def test_ca1007_url_analysis_presente(self, respuesta):
        """CA-10-07: La respuesta incluye el campo url_analysis con lista de URLs."""
        assert "url_analysis" in respuesta, "Falta campo url_analysis en la respuesta"
        assert "urls" in respuesta["url_analysis"]
        assert isinstance(respuesta["url_analysis"]["urls"], list)

    def test_ca1008_correo_phishing_activa_url_analizada(self, respuesta):
        """CA-10-08: Un correo phishing con URL activa al menos 1 URL analizada."""
        url_analysis = respuesta["url_analysis"]
        assert url_analysis["total_urls"] >= 1, (
            f"El correo phishing con URL no activo ningun analisis de URL: {url_analysis}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# MODULO B — Analisis masivo por lotes y panel de estadisticas (CA-10-09 a CA-10-18)
# ══════════════════════════════════════════════════════════════════════════════

class TestAnalisisPorLotesYEstadisticas:

    def test_ca1009_multiples_llamadas_independientes_retornan_resultados(self):
        """CA-10-09: POST /analyze/ acepta multiples llamadas independientes (lote)."""
        resultados = []
        for correo in LOTE:
            r = client.post("/analyze/", json=correo)
            assert r.status_code == 200, (
                f"Fallo en la llamada del lote para '{correo['subject']}': HTTP {r.status_code}"
            )
            resultados.append(r.json())
        assert len(resultados) == len(LOTE), (
            f"Se esperaban {len(LOTE)} resultados, se obtuvieron {len(resultados)}"
        )

    def test_ca1010_cada_resultado_tiene_label_propio(self):
        """CA-10-10: Cada resultado del lote tiene su propio label."""
        for correo in LOTE:
            data = client.post("/analyze/", json=correo).json()
            assert "label" in data
            assert data["label"] in ("phishing", "seguro"), (
                f"Label inesperado para '{correo['subject']}': {data['label']}"
            )

    def test_ca1011_lote_tres_correos_produce_tres_resultados(self):
        """CA-10-11: Procesar 3 correos en lote produce 3 resultados con confidence."""
        resultados = [
            client.post("/analyze/", json=c).json()
            for c in LOTE
        ]
        assert len(resultados) == 3
        for res in resultados:
            assert "confidence" in res
            assert 0.0 <= res["confidence"] <= 1.0

    def test_ca1012_tiempo_respuesta_por_correo_menor_5s(self):
        """CA-10-12: El tiempo de respuesta por correo analizado es menor a 5 segundos."""
        inicio = time.perf_counter()
        client.post("/analyze/", json=PHISHING_CON_URL)
        duracion = time.perf_counter() - inicio
        assert duracion < 5.0, (
            f"El endpoint tardo {duracion:.2f}s — maximo aceptable para lote: 5s por correo"
        )

    def test_ca1013_stats_retorna_conteos_principales(self):
        """CA-10-13: GET /stats/ retorna total, phishing_count y safe_count."""
        client.post("/analyze/", json=PHISHING_CON_URL)
        r = client.get("/stats/")
        assert r.status_code == 200
        data = r.json()
        for campo in ("total", "phishing_count", "safe_count"):
            assert campo in data, f"Falta campo '{campo}' en /stats/"
            assert isinstance(data[campo], int)

    def test_ca1014_stats_retorna_promedios_de_confianza_y_tiempo(self):
        """CA-10-14: GET /stats/ retorna avg_confidence y avg_response_ms."""
        r = client.get("/stats/")
        data = r.json()
        assert "avg_confidence"  in data, "Falta avg_confidence en /stats/"
        assert "avg_response_ms" in data, "Falta avg_response_ms en /stats/"
        if data["avg_confidence"] is not None:
            assert 0.0 <= data["avg_confidence"] <= 1.0

    def test_ca1015_stats_retorna_distribucion_de_riesgo(self):
        """CA-10-15: GET /stats/ retorna risk_distribution con niveles alto, medio y bajo."""
        r = client.get("/stats/")
        data = r.json()
        assert "risk_distribution" in data, "Falta risk_distribution en /stats/"
        dist = data["risk_distribution"]
        for nivel in ("alto", "medio", "bajo"):
            assert nivel in dist, f"Falta nivel '{nivel}' en risk_distribution"

    def test_ca1016_stats_retorna_tendencia_diaria(self):
        """CA-10-16: GET /stats/ retorna daily_trend como lista de registros diarios."""
        r = client.get("/stats/")
        data = r.json()
        assert "daily_trend" in data, "Falta daily_trend en /stats/"
        assert isinstance(data["daily_trend"], list), (
            "daily_trend debe ser una lista"
        )

    def test_ca1017_stats_retorna_campos_de_feedback(self):
        """CA-10-17: GET /stats/ retorna feedback_total y feedback_corrections."""
        r = client.get("/stats/")
        data = r.json()
        assert "feedback_total"       in data, "Falta feedback_total en /stats/"
        assert "feedback_corrections" in data, "Falta feedback_corrections en /stats/"
        assert data["feedback_total"] >= data["feedback_corrections"]

    def test_ca1018_stats_incrementa_tras_nuevos_analisis(self):
        """CA-10-18: El total en /stats/ se incrementa tras nuevos analisis."""
        antes = client.get("/stats/").json()["total"]
        client.post("/analyze/", json=SEGURO)
        client.post("/analyze/", json=PHISHING_CON_URL)
        despues = client.get("/stats/").json()["total"]
        assert despues >= antes + 2, (
            f"El total no incremento: antes={antes}, despues={despues}"
        )
