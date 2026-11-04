import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.data.parser import from_text, _extract_domain, ParsedEmail


def test_from_text_returns_parsed_email():
    text = "Estimado cliente, haz clic en https://fake-bank.com para verificar"
    result = from_text(text)
    assert isinstance(result, ParsedEmail)
    assert result.body == text
    assert "https://fake-bank.com" in result.urls


def test_from_text_extracts_multiple_urls():
    text = "Visita https://a.com y también http://b.org para continuar"
    result = from_text(text)
    assert len(result.urls) == 2


def test_extract_domain():
    assert _extract_domain("soporte@banco.com.co") == "banco.com.co"
    assert _extract_domain("Banco Falso <noreply@fake.net>") == "fake.net"
    assert _extract_domain("sin-dominio") == ""


def test_domain_mismatch_detection():
    email = ParsedEmail(
        sender="Bancolombia <noreply@bancolombia.com>",
        return_path="<bounce@phisher-domain.ru>",
    )
    assert email.domain_mismatch is True


def test_no_domain_mismatch_on_same_domain():
    email = ParsedEmail(
        sender="noreply@bancolombia.com",
        return_path="<noreply@bancolombia.com>",
    )
    assert email.domain_mismatch is False


def test_full_text_combines_subject_and_body():
    email = ParsedEmail(subject="Alerta de seguridad", body="Su cuenta fue bloqueada")
    assert "Alerta de seguridad" in email.full_text
    assert "bloqueada" in email.full_text
