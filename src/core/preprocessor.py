import re
import unicodedata
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer

from config.settings import LANGUAGE, URGENCY_KEYWORDS, CONTEXT_SENSITIVE_KEYWORDS, CONTEXT_WINDOW_CHARS

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)

_STOP_WORDS: set[str] = set(stopwords.words(LANGUAGE))
_STEMMER = SnowballStemmer(LANGUAGE)

_URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
_EMAIL_PATTERN = re.compile(r"[\w.-]+@[\w.-]+\.\w+")
_HTML_PATTERN = re.compile(r"<[^>]+>")
_NON_ALPHA = re.compile(r"[^a-záéíóúüñ\s]")
_MULTI_SPACE = re.compile(r"\s+")


def normalize(text: str) -> str:
    text = text.lower()
    text = unicodedata.normalize("NFC", text)
    return text


def strip_html(text: str) -> str:
    return _HTML_PATTERN.sub(" ", text)


def extract_urls(text: str) -> list[str]:
    return _URL_PATTERN.findall(text)


def remove_urls(text: str) -> str:
    return _URL_PATTERN.sub(" URL ", text)


def remove_emails(text: str) -> str:
    return _EMAIL_PATTERN.sub(" EMAIL ", text)


def clean(text: str) -> str:
    text = strip_html(text)
    text = remove_urls(text)
    text = remove_emails(text)
    text = normalize(text)
    text = _NON_ALPHA.sub(" ", text)
    text = _MULTI_SPACE.sub(" ", text).strip()
    return text


def tokenize(text: str) -> list[str]:
    return word_tokenize(text, language=LANGUAGE)


def remove_stopwords(tokens: list[str]) -> list[str]:
    return [t for t in tokens if t not in _STOP_WORDS and len(t) > 2]


def stem(tokens: list[str]) -> list[str]:
    return [_STEMMER.stem(t) for t in tokens]


def preprocess(text: str, apply_stemming: bool = False) -> str:
    cleaned = clean(text)
    tokens = tokenize(cleaned)
    tokens = remove_stopwords(tokens)
    if apply_stemming:
        tokens = stem(tokens)
    return " ".join(tokens)


def detect_urgency_keywords(text: str) -> list[str]:
    text_lower = text.lower()
    found: list[str] = []

    # 1. Palabras inherentemente sospechosas (siempre cuentan)
    found.extend(kw for kw in URGENCY_KEYWORDS if kw in text_lower)

    # 2. Palabras contextuales: solo cuentan cuando aparecen junto a un verbo de acción sospechoso
    for word, triggers in CONTEXT_SENSITIVE_KEYWORDS.items():
        pos = text_lower.find(word)
        while pos != -1:
            start = max(0, pos - CONTEXT_WINDOW_CHARS)
            end = min(len(text_lower), pos + len(word) + CONTEXT_WINDOW_CHARS)
            window = text_lower[start:end]
            if any(trigger in window for trigger in triggers):
                found.append(word)
                break  # contar solo una vez por palabra
            pos = text_lower.find(word, pos + 1)

    return found
