"""
Pruebas de aceptacion — HU-08: Implementacion de explicabilidad XAI
====================================================================
Criterio oficial:
    "Top-N terminos TF-IDF ponderados visibles en la interfaz
     y palabras de ingenieria social detectadas en el texto analizado."

Cobertura:
    CA-08-01  explain() retorna ExplainabilityReport con todos los campos
    CA-08-02  top_phishing_features contiene hasta XAI_TOP_FEATURES terminos
    CA-08-03  cada termino de top_phishing_features tiene peso > 0
    CA-08-04  urgency_keywords_found detecta palabras en texto de phishing
    CA-08-05  urgency_keywords_found esta vacio en texto limpio
    CA-08-06  social_engineering_score esta en rango [0.0, 1.0]
    CA-08-07  social_engineering_score alto en texto con muchas palabras de urgencia
    CA-08-08  social_engineering_score cero en texto sin palabras de urgencia
    CA-08-09  summary es una cadena no vacia
    CA-08-10  summary menciona palabras de urgencia cuando existen
    CA-08-11  endpoint POST /analyze/ incluye campo explainability en respuesta
    CA-08-12  explainability contiene los cuatro subcampos requeridos
    CA-08-13  top_phishing_features en API tiene estructura word + weight
    CA-08-14  XAI funciona con texto en espanol (sin traduccion)
"""
from __future__ import annotations

import sys
from pathlib import Path

import joblib
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from config.settings import ACTIVE_MODEL_FILE, VECTORIZER_FILE, XAI_TOP_FEATURES
from src.core.explainer import explain, ExplainabilityReport
from src.core.preprocessor import preprocess
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

PHISHING_TEXT = (
    "Estimado cliente, su cuenta bancaria ha sido SUSPENDIDA por actividad sospechosa. "
    "Verifique INMEDIATAMENTE sus datos en http://banco-bogota-seguro.verificar-cuenta.net "
    "Ingrese su cedula, clave y PIN. Si no confirma en 24 horas su cuenta sera CANCELADA."
)

SAFE_TEXT = (
    "Hola, tu extracto de agosto esta disponible en la sucursal virtual. "
    "Saldo final: 3.990.000 COP. Para consultarlo ingresa con tus datos habituales. "
    "Davivienda. Entidad vigilada por la Superfinanciera."
)


@pytest.fixture(scope="module")
def vectorizer():
    return joblib.load(VECTORIZER_FILE)


@pytest.fixture(scope="module")
def xai_phishing(vectorizer):
    return explain(PHISHING_TEXT, preprocess(PHISHING_TEXT), vectorizer)


@pytest.fixture(scope="module")
def xai_safe(vectorizer):
    return explain(SAFE_TEXT, preprocess(SAFE_TEXT), vectorizer)


# CA-08-01 a CA-08-03: estructura del reporte
class TestEstructuraReporte:

    def test_ca0801_retorna_explainability_report(self, xai_phishing):
        """CA-08-01: explain() retorna una instancia de ExplainabilityReport."""
        assert isinstance(xai_phishing, ExplainabilityReport)

    def test_ca0802_top_features_tiene_n_terminos(self, xai_phishing):
        """CA-08-02: top_phishing_features contiene hasta XAI_TOP_FEATURES terminos."""
        assert len(xai_phishing.top_phishing_features) <= XAI_TOP_FEATURES
        assert len(xai_phishing.top_phishing_features) > 0

    def test_ca0803_pesos_son_positivos(self, xai_phishing):
        """CA-08-03: Todos los terminos tienen peso mayor a cero."""
        for word, weight in xai_phishing.top_phishing_features:
            assert weight > 0, f"El termino '{word}' tiene peso {weight}"


# CA-08-04 a CA-08-08: palabras de urgencia e ingenieria social
class TestIngenieriaSocial:

    def test_ca0804_detecta_urgencia_en_phishing(self, xai_phishing):
        """CA-08-04: urgency_keywords_found detecta palabras en correo de phishing."""
        assert len(xai_phishing.urgency_keywords_found) > 0

    def test_ca0805_sin_urgencia_en_texto_seguro(self, xai_safe):
        """CA-08-05: urgency_keywords_found esta vacio en correo seguro."""
        assert isinstance(xai_safe.urgency_keywords_found, list)
        assert len(xai_safe.urgency_keywords_found) == 0

    def test_ca0806_social_score_en_rango(self, xai_phishing):
        """CA-08-06: social_engineering_score esta en [0.0, 1.0]."""
        assert 0.0 <= xai_phishing.social_engineering_score <= 1.0

    def test_ca0807_social_score_alto_en_phishing(self, xai_phishing):
        """CA-08-07: social_engineering_score es alto en texto de phishing con urgencia."""
        assert xai_phishing.social_engineering_score > 0.0

    def test_ca0808_social_score_cero_en_seguro(self, xai_safe):
        """CA-08-08: social_engineering_score es cero en texto sin palabras de urgencia."""
        assert xai_safe.social_engineering_score == 0.0


# CA-08-09 a CA-08-10: resumen
class TestResumen:

    def test_ca0809_summary_no_vacio(self, xai_phishing):
        """CA-08-09: summary es una cadena no vacia."""
        assert isinstance(xai_phishing.summary, str)
        assert len(xai_phishing.summary) > 0

    def test_ca0810_summary_menciona_urgencia(self, xai_phishing):
        """CA-08-10: summary menciona palabras de urgencia cuando existen."""
        assert any(kw in xai_phishing.summary for kw in xai_phishing.urgency_keywords_found)


# CA-08-11 a CA-08-14: integracion con API
class TestXAIEnAPI:

    def test_ca0811_api_incluye_explainability(self):
        """CA-08-11: POST /analyze/ incluye el campo explainability en la respuesta."""
        data = client.post("/analyze/", json={"text": PHISHING_TEXT}).json()
        assert "explainability" in data

    def test_ca0812_explainability_tiene_subcampos(self):
        """CA-08-12: explainability contiene los cuatro subcampos requeridos."""
        xai = client.post("/analyze/", json={"text": PHISHING_TEXT}).json()["explainability"]
        for campo in ["top_phishing_features", "urgency_keywords_found",
                      "social_engineering_score", "summary"]:
            assert campo in xai, f"Falta el subcampo '{campo}' en explainability"

    def test_ca0813_top_features_tiene_estructura_correcta(self):
        """CA-08-13: Cada elemento de top_phishing_features tiene word y weight."""
        xai = client.post("/analyze/", json={"text": PHISHING_TEXT}).json()["explainability"]
        features = xai["top_phishing_features"]
        assert len(features) > 0
        for f in features:
            assert "word" in f
            assert "weight" in f
            assert f["weight"] > 0

    def test_ca0814_xai_funciona_con_espanol(self):
        """CA-08-14: XAI produce resultados validos con texto en espanol."""
        data = client.post("/analyze/", json={"text": PHISHING_TEXT}).json()
        xai = data["explainability"]
        assert xai["social_engineering_score"] >= 0.0
        assert isinstance(xai["urgency_keywords_found"], list)
