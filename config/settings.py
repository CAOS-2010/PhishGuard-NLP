import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Paths
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
MODELS_DIR = BASE_DIR / "models"
HISTORY_DB = BASE_DIR / "history.db"

# Model filenames
VECTORIZER_FILE = MODELS_DIR / "tfidf_vectorizer.joblib"
CLASSIFIER_RF_FILE = MODELS_DIR / "random_forest.joblib"
CLASSIFIER_SVM_FILE = MODELS_DIR / "svm.joblib"
ACTIVE_MODEL_FILE = MODELS_DIR / "active_model.joblib"

# NLP
LANGUAGE = "spanish"
MAX_FEATURES = 10_000
NGRAM_RANGE = (1, 2)

# Model training
TEST_SIZE = 0.2
RANDOM_STATE = 42
CV_FOLDS = 5

# Risk thresholds (probability of phishing)
RISK_LOW = 0.35
RISK_HIGH = 0.70
# Decision threshold: minimum probability to label a message as phishing.
# Higher than RISK_LOW to avoid false positives on legitimate banking emails
# whose vocabulary partially overlaps with the phishing training corpus.
DECISION_THRESHOLD = 0.70

# API
API_HOST = os.environ.get("API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("PORT", os.environ.get("API_PORT", "8036")))
API_BASE_URL = os.environ.get("API_BASE_URL", f"http://127.0.0.1:{API_PORT}")

# XAI — top N features to display
XAI_TOP_FEATURES = 15

# Palabras de urgencia inherentemente sospechosas (siempre cuentan)
URGENCY_KEYWORDS: list[str] = [
    # Urgencia temporal
    "urgente", "inmediatamente", "vence", "expira",
    "bloqueada", "suspendida", "cancelada", "restringida", "limitada",
    # Alertas
    "alerta", "advertencia", "peligro",
    # Llamadas a la acción directas
    "haga clic", "click aquí", "pulse aquí",
    # Premios y regalos (siempre sospechosos en correo)
    "premio", "ganador", "recompensa", "gratis",
    # Solicitud explícita de datos sensibles (frases, no palabras sueltas)
    "datos bancarios", "numero de cuenta", "número de cuenta",
    "copia de cédula", "copia de cedula",
    "cuenta bancaria", "clave bancaria",
    "formulario adjunto", "formulario con sus datos",
    # Patrones de estafa financiera
    "herencia", "beneficiario", "fondos retenidos", "fondos bloqueados",
    "impuesto de liberación", "impuesto de liberacion", "comisión de liberación",
    "seleccionado para recibir", "ganó el sorteo", "gano el sorteo",
    # Patrones de empleo falso
    "pague el examen", "deposite la garantía", "deposite la garantia",
    "kit de dotación", "estudio de seguridad",
]

# Palabras contextuales: solo cuentan si aparecen cerca de un verbo de acción sospechoso.
# Formato: {palabra: [verbos_de_accion_sospechosos]}
# Distingue "ingresa al sistema con tu contraseña" (legítimo) de
# "proporcione su contraseña para verificar" (phishing).
CONTEXT_SENSITIVE_KEYWORDS: dict[str, list[str]] = {
    "contraseña": [
        "proporcione", "envíe", "envie", "confirme su contraseña",
        "ingrese su contraseña", "ingresa tu contraseña",
        "escriba su contraseña", "introduzca su contraseña",
    ],
    "clave": [
        "proporcione", "envíe", "envie", "confirme su clave",
        "ingrese su clave", "ingresa tu clave",
        "escriba su clave", "introduzca su clave",
    ],
    "pin": [
        "proporcione", "envíe", "envie", "ingrese su pin",
        "confirme su pin", "ingresa tu pin",
    ],
    "usuario": [
        "proporcione su usuario", "envíe su usuario",
        "ingrese su usuario y contraseña para verificar",
        "ingrese su nombre de usuario",
    ],
    "cuenta": [
        "proporcione su cuenta", "envíe su cuenta",
        "ingrese su número de cuenta", "datos de su cuenta bancaria",
        "adjunte su cuenta",
    ],
    "transferencia": [
        "transferencia urgente", "transferencia inmediata",
        "transferencia internacional", "realizar una transferencia",
        "realizar el pago por transferencia",
    ],
}

# Ventana de caracteres a cada lado de la palabra para buscar el verbo de acción
CONTEXT_WINDOW_CHARS: int = 120
