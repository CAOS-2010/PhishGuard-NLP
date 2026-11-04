"""
Convierte datasets públicos al formato estándar del proyecto: columnas 'text' y 'label' (0/1).

Datasets soportados (todos de Kaggle):

  1. subhajournal/phishingemails  (RECOMENDADO)
     Archivo: Phishing_Email.csv
     Columnas originales: 'Email Text', 'Email Type' (Safe Email / Phishing Email)

  2. naserabdullahalam/phishing-email-dataset
     Archivo: SpamAssasin.csv  o  CEAS_08.csv
     Columnas originales: 'body', 'label' (1=spam, 0=ham)

  3. kuladeep19/phishing-and-legitimate-emails-dataset
     Columnas originales: 'email_text', 'label' (1=phishing, 0=legit)

Uso:
    python scripts/prepare_dataset.py --input data/raw/<archivo>.csv --format subhajournal
    python scripts/prepare_dataset.py --input data/raw/<archivo>.csv --format naser
    python scripts/prepare_dataset.py --input data/raw/<archivo>.csv --format kuladeep
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from config.settings import DATA_PROCESSED_DIR, DATA_RAW_DIR

OUTPUT_PATH = DATA_RAW_DIR / "dataset.csv"


def adapt_subhajournal(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={"Email Text": "text", "Email Type": "label"})
    df["label"] = df["label"].map({"Phishing Email": 1, "Safe Email": 0})
    return df[["text", "label"]]


def adapt_naser(df: pd.DataFrame) -> pd.DataFrame:
    # SpamAssasin.csv y CEAS_08.csv usan 'body' y 'label' (1=spam=phishing, 0=ham=seguro)
    col_text = "body" if "body" in df.columns else "text"
    df = df.rename(columns={col_text: "text"})
    df["label"] = pd.to_numeric(df["label"], errors="coerce")
    return df[["text", "label"]]


def adapt_kuladeep(df: pd.DataFrame) -> pd.DataFrame:
    col_text = "email_text" if "email_text" in df.columns else "text"
    df = df.rename(columns={col_text: "text"})
    df["label"] = pd.to_numeric(df["label"], errors="coerce")
    return df[["text", "label"]]


ADAPTERS = {
    "subhajournal": adapt_subhajournal,
    "naser": adapt_naser,
    "kuladeep": adapt_kuladeep,
}


def prepare(input_path: Path, fmt: str) -> None:
    if fmt not in ADAPTERS:
        print(f"Formato '{fmt}' no reconocido. Opciones: {list(ADAPTERS.keys())}")
        sys.exit(1)

    print(f"Cargando: {input_path}")
    df = pd.read_csv(input_path, encoding="utf-8", on_bad_lines="skip")
    print(f"Registros crudos: {len(df)}")

    df = ADAPTERS[fmt](df)
    df = df.dropna(subset=["text", "label"])
    df["text"] = df["text"].astype(str).str.strip()
    df = df[df["text"].str.len() > 20]
    df["label"] = df["label"].astype(int)
    df = df[df["label"].isin([0, 1])]
    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)

    print(f"Registros limpios: {len(df)}")
    print(f"Distribución:\n{df['label'].value_counts().rename({0: 'Seguro', 1: 'Phishing'}).to_string()}")

    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
    print(f"\nDataset guardado en: {OUTPUT_PATH}")
    print("Siguiente paso: python scripts/train_model.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepara el dataset para PhishGuard NLP")
    parser.add_argument("--input", required=True, help="Ruta al CSV descargado de Kaggle")
    parser.add_argument(
        "--format",
        required=True,
        choices=list(ADAPTERS.keys()),
        help="Formato del dataset origen",
    )
    args = parser.parse_args()
    prepare(Path(args.input), args.format)
