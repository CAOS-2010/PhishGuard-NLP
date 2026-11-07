from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

# Detecta URLs con y sin protocolo
_URL_RE = re.compile(
    r"(?:https?://|www\.)"              # con protocolo o www
    r"[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+"
    r"|"
    r"(?:[a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,6}"  # dominio multi-nivel sin protocolo
    r"(?:/[^\s\"<>]*)?"
)

_SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd",
    "buff.ly", "short.io", "rebrand.ly", "cutt.ly", "bl.ink",
}

_SUSPICIOUS_TLDS = {
    ".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".pw", ".top",
    ".club", ".click", ".link", ".live", ".online", ".site",
    ".zya.me", ".000webhostapp.com", ".glitch.me", ".ngrok.io",
}

_SUSPICIOUS_KEYWORDS = {
    "verify", "verification", "verificar", "verificacion",
    "login", "signin", "sign-in", "log-in",
    "secure", "security", "seguro", "seguridad",
    "update", "actualizar", "account", "cuenta",
    "confirm", "confirmar", "validation", "validar",
    "banking", "banco", "password", "contrasena",
    "credential", "credentials", "acceso", "access",
    "alert", "alerta", "warning", "urgent", "urgente",
    "suspend", "suspender", "blocked", "bloqueado",
    "support", "soporte", "helpdesk", "reset",
}

_KNOWN_BRANDS = [
    "bancolombia", "davivienda", "bbva", "nequi", "daviplata",
    "microsoft", "office365", "outlook", "hotmail", "microsoft365",
    "google", "gmail", "facebook", "instagram", "whatsapp",
    "apple", "icloud", "paypal", "amazon", "netflix",
    "tdea", "unal", "udea", "eafit", "javeriana",
]


@dataclass
class URLRisk:
    url: str
    uses_http: bool = False
    is_ip_based: bool = False
    is_shortener: bool = False
    suspicious_keywords: list[str] = field(default_factory=list)
    brand_spoofing: list[str] = field(default_factory=list)
    suspicious_tld: bool = False
    excessive_subdomains: bool = False
    risk_score: float = 0.0
    risk_level: str = "bajo"


@dataclass
class URLAnalysisReport:
    urls: list[URLRisk] = field(default_factory=list)
    total_urls: int = 0
    high_risk_urls: int = 0
    url_risk_score: float = 0.0


def _normalize_url(raw: str) -> str:
    # Strip trailing punctuation that belongs to surrounding prose, not the URL
    raw = raw.rstrip(".,;:)>\"'")
    if not raw.startswith(("http://", "https://")):
        return "http://" + raw
    return raw


def _extract_domain(url: str) -> str:
    try:
        return urlparse(_normalize_url(url)).netloc.lower()
    except Exception:
        return ""


def _extract_urls(text: str) -> list[str]:
    found = _URL_RE.findall(text)
    # Filtrar falsos positivos (palabras comunes con punto)
    filtered = []
    for u in found:
        domain = _extract_domain(u)
        if len(domain) > 4 and "." in domain:
            filtered.append(u)
    return list(dict.fromkeys(filtered))  # eliminar duplicados


def _analyze_single_url(raw_url: str) -> URLRisk:
    url = _normalize_url(raw_url)  # trailing punctuation already stripped
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    full = url.lower()

    result = URLRisk(url=raw_url)

    # 1. HTTP sin cifrado
    result.uses_http = url.startswith("http://")

    # 2. IP como dominio
    result.is_ip_based = bool(re.match(r"^\d{1,3}(\.\d{1,3}){3}$", domain.split(":")[0]))

    # 3. Acortador de URLs (coincidencia exacta, no subcadena)
    result.is_shortener = domain in _SHORTENERS or any(domain.endswith("." + s) for s in _SHORTENERS)

    # 4. Palabras sospechosas en dominio o ruta
    result.suspicious_keywords = [
        kw for kw in _SUSPICIOUS_KEYWORDS if kw in full
    ]

    # 5. Suplantación de marca (dominio contiene nombre de marca pero no es el dominio oficial)
    spoofed = []
    for brand in _KNOWN_BRANDS:
        if brand in domain:
            official_variants = (
                f"{brand}.com",
                f"{brand}.com.co",
                f"{brand}.co",
                f"{brand}.net",
                f"{brand}.org",
                f"{brand}.edu.co",
            )
            is_official = any(
                domain == v
                or domain == f"www.{v}"
                or domain.endswith(f".{v}")
                for v in official_variants
            )
            if not is_official:
                spoofed.append(brand)
    result.brand_spoofing = spoofed

    # 6. TLD sospechoso
    result.suspicious_tld = any(domain.endswith(tld) for tld in _SUSPICIOUS_TLDS)

    # 7. Exceso de subdominios (más de 3 niveles)
    result.excessive_subdomains = domain.count(".") >= 3

    # Calcular puntaje
    score = 0.0
    if result.uses_http:          score += 0.10
    if result.is_ip_based:        score += 0.30
    if result.is_shortener:       score += 0.20
    if result.suspicious_keywords:score += min(len(result.suspicious_keywords) * 0.08, 0.25)
    if result.brand_spoofing:     score += 0.30
    if result.suspicious_tld:     score += 0.25
    if result.excessive_subdomains: score += 0.15

    result.risk_score = round(min(score, 1.0), 3)
    result.risk_level = (
        "alto"  if result.risk_score >= 0.45 else
        "medio" if result.risk_score >= 0.20 else
        "bajo"
    )
    return result


def analyze_urls(text: str) -> URLAnalysisReport:
    raw_urls = _extract_urls(text)
    analyzed = [_analyze_single_url(u) for u in raw_urls]
    high_risk = [u for u in analyzed if u.risk_level == "alto"]
    score = max((u.risk_score for u in analyzed), default=0.0)
    return URLAnalysisReport(
        urls=analyzed,
        total_urls=len(analyzed),
        high_risk_urls=len(high_risk),
        url_risk_score=round(score, 3),
    )
