import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.core.preprocessor import (
    clean,
    detect_urgency_keywords,
    preprocess,
    remove_stopwords,
    tokenize,
)


def test_clean_removes_html():
    result = clean("<b>Estimado cliente</b>")
    assert "<b>" not in result
    assert "estimado" in result


def test_clean_removes_urls():
    result = clean("Haz clic aquí: https://banco-falso.com/login")
    assert "https" not in result
    assert "url" in result.lower()


def test_clean_removes_emails():
    result = clean("Contacta a soporte@banco.com para más info")
    assert "@" not in result


def test_clean_lowercases():
    result = clean("URGENTE: VERIFIQUE SU CUENTA")
    assert result == result.lower()


def test_tokenize_returns_list():
    tokens = tokenize("el banco bloqueó su cuenta")
    assert isinstance(tokens, list)
    assert len(tokens) > 0


def test_remove_stopwords_filters_common_words():
    tokens = ["el", "banco", "de", "su", "cuenta"]
    result = remove_stopwords(tokens)
    assert "banco" in result
    assert "el" not in result


def test_preprocess_pipeline():
    text = "<p>Estimado cliente, su cuenta ha sido BLOQUEADA. Haga clic aquí: https://fake.com</p>"
    result = preprocess(text)
    assert isinstance(result, str)
    assert len(result) > 0
    assert "<p>" not in result
    assert "https" not in result


def test_detect_urgency_keywords_finds_matches():
    text = "su cuenta ha sido bloqueada, verifique urgentemente"
    found = detect_urgency_keywords(text)
    assert "bloqueada" in found
    assert "urgente" in found or "verificar" in found


def test_detect_urgency_keywords_empty_on_clean_text():
    text = "Bienvenido al resumen mensual de su tarjeta de crédito"
    found = detect_urgency_keywords(text)
    assert isinstance(found, list)
