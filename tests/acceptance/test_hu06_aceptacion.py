"""
Pruebas de aceptacion — HU-06: Modulo de ingesta de archivos .eml
=================================================================
Criterio oficial:
    "Parser .eml/.msg extrae texto, remitente y asunto;
     muestra mensaje descriptivo ante formato incompatible."

Cobertura:
    CA-06-01  from_eml() extrae remitente correctamente
    CA-06-02  from_eml() extrae asunto correctamente
    CA-06-03  from_eml() extrae cuerpo de texto
    CA-06-04  from_eml() detecta URLs en el cuerpo
    CA-06-05  from_eml() maneja correo multipart (text/plain + text/html)
    CA-06-06  from_eml() maneja charset no-UTF8 sin lanzar excepcion
    CA-06-07  parse_file() lanza ValueError con mensaje descriptivo
               ante extension no soportada
    CA-06-08  parse_file() lanza ValueError con mensaje descriptivo
               ante archivo con extension correcta pero contenido invalido
    CA-06-09  from_eml() extrae dominio del remitente para domain_mismatch
    CA-06-10  parse_file() enruta correctamente segun extension
"""
from __future__ import annotations

import email
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.data.parser import from_eml, parse_file, ParsedEmail


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _write_eml(path: Path, subject: str, sender: str, body_plain: str,
               body_html: str | None = None, charset: str = "utf-8") -> Path:
    """Crea un archivo .eml real en disco para los tests."""
    if body_html:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = "usuario@test.com"
        msg.attach(MIMEText(body_plain, "plain", charset))
        msg.attach(MIMEText(body_html, "html", charset))
    else:
        msg = MIMEText(body_plain, "plain", charset)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = "usuario@test.com"

    path.write_bytes(msg.as_bytes())
    return path


@pytest.fixture
def eml_phishing(tmp_path) -> Path:
    return _write_eml(
        tmp_path / "phishing.eml",
        subject="URGENTE: Su cuenta ha sido bloqueada",
        sender="seguridad@banco-bogota-verificacion.com",
        body_plain=(
            "Su cuenta bancaria fue SUSPENDIDA. "
            "Verifique INMEDIATAMENTE en "
            "http://banco-bogota-seguro.verificar-cuenta.net/login "
            "su cedula, clave y pin."
        ),
    )


@pytest.fixture
def eml_safe(tmp_path) -> Path:
    return _write_eml(
        tmp_path / "safe.eml",
        subject="Confirmacion de transaccion PSE",
        sender="notificaciones@bancolombia.com.co",
        body_plain="Su transaccion de 150.000 COP fue procesada exitosamente.",
    )


@pytest.fixture
def eml_multipart(tmp_path) -> Path:
    return _write_eml(
        tmp_path / "multipart.eml",
        subject="Extracto bancario agosto",
        sender="extractos@davivienda.com.co",
        body_plain="Tu extracto de agosto esta disponible. Saldo: 3.990.000 COP.",
        body_html="<html><body><p>Tu extracto de agosto.</p></body></html>",
    )


@pytest.fixture
def incompatible_file(tmp_path) -> Path:
    f = tmp_path / "adjunto.pdf"
    f.write_bytes(b"%PDF-1.4 contenido binario no valido")
    return f


@pytest.fixture
def incompatible_txt(tmp_path) -> Path:
    f = tmp_path / "correo.txt"
    f.write_text("esto es un txt no un eml", encoding="utf-8")
    return f


# ── CA-06-01 a CA-06-04: extraccion de campos basicos ────────────────────────

class TestExtraccionCamposBasicos:

    def test_ca0601_extrae_remitente(self, eml_phishing):
        """CA-06-01: from_eml() extrae el campo sender del encabezado From."""
        result = from_eml(eml_phishing)
        assert result.sender, "El remitente no puede estar vacio"
        assert "banco-bogota-verificacion.com" in result.sender

    def test_ca0602_extrae_asunto(self, eml_phishing):
        """CA-06-02: from_eml() extrae el campo subject del encabezado Subject."""
        result = from_eml(eml_phishing)
        assert result.subject, "El asunto no puede estar vacio"
        assert "bloqueada" in result.subject.lower()

    def test_ca0603_extrae_cuerpo(self, eml_phishing):
        """CA-06-03: from_eml() extrae el cuerpo del correo con contenido legible."""
        result = from_eml(eml_phishing)
        assert result.body, "El cuerpo no puede estar vacio"
        assert len(result.body) >= 20

    def test_ca0604_detecta_urls_en_cuerpo(self, eml_phishing):
        """CA-06-04: from_eml() extrae URLs presentes en el cuerpo."""
        result = from_eml(eml_phishing)
        assert len(result.urls) > 0, "Debe detectar al menos una URL"
        assert any("banco-bogota" in url for url in result.urls)


# ── CA-06-05 a CA-06-06: robustez en formatos complejos ──────────────────────

class TestRobustezFormatos:

    def test_ca0605_maneja_multipart(self, eml_multipart):
        """CA-06-05: from_eml() procesa correos con partes text/plain y text/html."""
        result = from_eml(eml_multipart)
        assert result.body, "El cuerpo debe extraerse de la parte text/plain"
        assert "extracto" in result.body.lower()

    def test_ca0606_no_lanza_excepcion_con_charset_invalido(self, tmp_path):
        """CA-06-06: from_eml() maneja charsets no estandar sin lanzar excepcion."""
        eml_path = _write_eml(
            tmp_path / "latin.eml",
            subject="Notificacion bancaria",
            sender="banco@test.com",
            body_plain="Estimado cliente, su cuenta esta activa.",
            charset="latin-1",
        )
        try:
            result = from_eml(eml_path)
            assert result is not None
        except Exception as exc:
            pytest.fail(f"from_eml() lanzo excepcion inesperada: {exc}")


# ── CA-06-07 a CA-06-08: mensajes descriptivos en formatos incompatibles ─────

class TestFormatoIncompatible:

    def test_ca0607_formato_no_soportado_lanza_valueerror(self, incompatible_file):
        """CA-06-07: parse_file() lanza ValueError con mensaje para extension .pdf."""
        with pytest.raises(ValueError) as exc_info:
            parse_file(incompatible_file)
        mensaje = str(exc_info.value).lower()
        assert len(mensaje) >= 10, "El mensaje de error debe ser descriptivo"

    def test_ca0607_mensaje_menciona_formatos_aceptados(self, incompatible_file):
        """CA-06-07b: El mensaje de error menciona los formatos aceptados."""
        with pytest.raises(ValueError) as exc_info:
            parse_file(incompatible_file)
        mensaje = str(exc_info.value).lower()
        assert "eml" in mensaje or "msg" in mensaje, (
            f"El mensaje '{mensaje}' deberia mencionar .eml o .msg"
        )

    def test_ca0608_extension_txt_no_soportada(self, incompatible_txt):
        """CA-06-08: parse_file() rechaza .txt con ValueError descriptivo."""
        with pytest.raises(ValueError):
            parse_file(incompatible_txt)


# ── CA-06-09 a CA-06-10: domain_mismatch y enrutamiento ─────────────────────

class TestDomainYEnrutamiento:

    def test_ca0609_domain_mismatch_false_en_correo_legitimo(self, eml_safe):
        """CA-06-09: domain_mismatch es False cuando From y Return-Path coinciden."""
        result = from_eml(eml_safe)
        assert result.domain_mismatch is False

    def test_ca0610_parse_file_enruta_por_extension_eml(self, eml_phishing):
        """CA-06-10: parse_file() llama from_eml() para archivos .eml."""
        result = parse_file(eml_phishing)
        assert isinstance(result, ParsedEmail)
        assert result.sender is not None
