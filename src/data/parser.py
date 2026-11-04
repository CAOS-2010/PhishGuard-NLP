from __future__ import annotations

import email
import re
from dataclasses import dataclass, field
from pathlib import Path

_URL_RE = re.compile(r"https?://[^\s\"<>]+")


@dataclass
class ParsedEmail:
    subject: str = ""
    sender: str = ""
    return_path: str = ""
    body: str = ""
    urls: list[str] = field(default_factory=list)
    raw_headers: dict[str, str] = field(default_factory=dict)

    @property
    def full_text(self) -> str:
        return f"{self.subject} {self.body}".strip()

    @property
    def domain_mismatch(self) -> bool:
        sender_domain = _extract_domain(self.sender)
        rp_domain = _extract_domain(self.return_path)
        if not sender_domain or not rp_domain:
            return False
        return sender_domain != rp_domain


def _extract_domain(address: str) -> str:
    match = re.search(r"@([\w.-]+)", address)
    return match.group(1).lower() if match else ""


def from_text(text: str) -> ParsedEmail:
    urls = _URL_RE.findall(text)
    return ParsedEmail(body=text, urls=urls)


def _strip_html(html: str) -> str:
    text = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<script[^>]*>.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&[a-z]+;", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def from_eml(path: Path) -> ParsedEmail:
    raw = path.read_bytes()
    msg = email.message_from_bytes(raw)

    subject = msg.get("Subject", "")
    sender = msg.get("From", "")
    return_path = msg.get("Return-Path", sender)
    headers = {k: str(v) for k, v in msg.items()}

    plain_parts: list[str] = []
    html_parts: list[str] = []

    for part in msg.walk():
        ct = part.get_content_type()
        charset = part.get_content_charset() or "utf-8"
        try:
            payload = part.get_payload(decode=True).decode(charset, errors="replace")
        except Exception:
            continue
        if ct == "text/plain":
            plain_parts.append(payload)
        elif ct == "text/html":
            html_parts.append(payload)

    # Preferir texto plano; usar HTML solo si no hay texto plano
    if plain_parts:
        body = " ".join(plain_parts)
    elif html_parts:
        body = _strip_html(" ".join(html_parts))
    else:
        body = ""

    urls = _URL_RE.findall(body)

    return ParsedEmail(
        subject=subject,
        sender=sender,
        return_path=return_path,
        body=body,
        urls=urls,
        raw_headers=headers,
    )


def from_msg(path: Path) -> ParsedEmail:
    try:
        import extract_msg  # type: ignore
        msg = extract_msg.Message(str(path))
        body = msg.body or ""
        urls = _URL_RE.findall(body)
        return ParsedEmail(
            subject=msg.subject or "",
            sender=msg.sender or "",
            return_path=msg.sender or "",
            body=body,
            urls=urls,
        )
    except ImportError as exc:
        raise ImportError("Instala extract-msg: pip install extract-msg") from exc


def parse_file(path: Path) -> ParsedEmail:
    suffix = path.suffix.lower()
    if suffix == ".eml":
        return from_eml(path)
    if suffix == ".msg":
        return from_msg(path)
    raise ValueError(f"Formato no soportado: {suffix}. Usa .eml o .msg")
