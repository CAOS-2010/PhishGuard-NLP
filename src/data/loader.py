from __future__ import annotations

from pathlib import Path

import pandas as pd

from config.settings import DATA_RAW_DIR, DATA_PROCESSED_DIR
from src.core.preprocessor import preprocess

PROCESSED_CSV = DATA_PROCESSED_DIR / "dataset_processed.csv"

# Limites de longitud del texto crudo y procesado
_MIN_RAW_CHARS = 30
_MAX_RAW_CHARS = 10_000
_MIN_CLEAN_TOKENS = 5


def load_raw(path: Path | None = None) -> pd.DataFrame:
    csv_path = path or DATA_RAW_DIR / "dataset.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Dataset no encontrado en {csv_path}.\n"
            "Descarga un dataset de phishing desde Kaggle y coloca el archivo en data/raw/dataset.csv\n"
            "Columnas requeridas: 'text' (cuerpo del correo) y 'label' (0=seguro, 1=phishing)"
        )
    df = pd.read_csv(csv_path)
    _validate_columns(df)
    return df


def _validate_columns(df: pd.DataFrame) -> None:
    required = {"text", "label"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"El dataset debe tener las columnas: {required}. Faltan: {missing}"
        )


def clean_raw(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.copy()
    df["text"] = df["text"].astype(str).str.strip()

    # Eliminar textos vacios o nulos
    df = df[df["text"].notna() & (df["text"] != "") & (df["text"] != "nan")]

    # Eliminar textos demasiado cortos (sin contenido util)
    df = df[df["text"].str.len() >= _MIN_RAW_CHARS]

    # Eliminar outliers extremos (correos de mas de 10.000 chars distorsionan TF-IDF)
    df = df[df["text"].str.len() <= _MAX_RAW_CHARS]

    # Eliminar duplicados exactos
    df = df.drop_duplicates(subset=["text"])

    # Garantizar que el label sea binario
    df["label"] = pd.to_numeric(df["label"], errors="coerce")
    df = df[df["label"].isin([0, 1])].reset_index(drop=True)

    removed = before - len(df)
    print(f"      Limpieza raw: {before} -> {len(df)} registros ({removed} eliminados)")
    return df


def preprocess_and_save(df: pd.DataFrame) -> pd.DataFrame:
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    df = df.copy()

    df["text_clean"] = df["text"].astype(str).apply(preprocess)

    # Eliminar textos que quedaron vacios o con muy pocos tokens tras limpiar
    before = len(df)
    df = df[df["text_clean"].notna()]
    df = df[df["text_clean"].str.strip() != ""]
    df = df[df["text_clean"].str.split().str.len() >= _MIN_CLEAN_TOKENS]
    df = df.reset_index(drop=True)

    removed = before - len(df)
    if removed > 0:
        print(f"      Limpieza post-NLP: {before} -> {len(df)} registros ({removed} eliminados)")

    df.to_csv(PROCESSED_CSV, index=False)
    return df


def load_processed() -> pd.DataFrame:
    if not PROCESSED_CSV.exists():
        raise FileNotFoundError(
            "Dataset procesado no encontrado. Ejecuta scripts/train_model.py primero."
        )
    return pd.read_csv(PROCESSED_CSV)
