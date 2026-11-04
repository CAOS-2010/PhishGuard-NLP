"""
Combina los datasets disponibles en un corpus ampliado y reentrena el modelo.

Fuentes:
  - data/raw/dataset.csv                        (17 505 correos — base actual)
  - data/raw/Phishing_Email.csv                 (18 650 correos — phishing general)
  - data/raw/phishing_legit_dataset_KD_10000.csv(10 000 correos — 9 tipos de phishing)
  - data/raw/dataset_spanish.csv                (  400 correos — español)

Total esperado: ~46 000 correos tras limpieza de duplicados.

Uso:
    python scripts/expand_dataset.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

from config.settings import DATA_RAW_DIR

OUTPUT = DATA_RAW_DIR / "dataset.csv"
BACKUP = DATA_RAW_DIR / "dataset_backup_original.csv"


def load_dataset(path: Path, text_col: str, label_col: str,
                 label_map: dict | None = None) -> pd.DataFrame:
    df = pd.read_csv(path, on_bad_lines="skip")
    df = df.rename(columns={text_col: "text", label_col: "label"})
    if label_map:
        df["label"] = df["label"].map(label_map)
    df = df[["text", "label"]]
    df["label"] = pd.to_numeric(df["label"], errors="coerce")
    return df


def main() -> None:
    print("=" * 60)
    print("PhishGuard NLP — Expansion del dataset")
    print("=" * 60)

    # Respaldo del dataset original
    original = DATA_RAW_DIR / "dataset.csv"
    if original.exists() and not BACKUP.exists():
        import shutil
        shutil.copy(original, BACKUP)
        print(f"\nBackup guardado en: {BACKUP.name}")

    partes = []

    # 1. Dataset base actual
    print("\n[1/4] dataset.csv (base actual)...")
    df1 = load_dataset(DATA_RAW_DIR / "dataset.csv", "text", "label")
    print(f"      {len(df1)} registros — phishing: {df1['label'].sum()}, seguro: {(df1['label']==0).sum()}")
    partes.append(df1)

    # 2. Phishing_Email.csv — phishing general en inglés
    print("\n[2/4] Phishing_Email.csv...")
    df2 = load_dataset(
        DATA_RAW_DIR / "Phishing_Email.csv",
        text_col="Email Text",
        label_col="Email Type",
        label_map={"Phishing Email": 1, "Safe Email": 0},
    )
    print(f"      {len(df2)} registros — phishing: {df2['label'].sum()}, seguro: {(df2['label']==0).sum()}")
    partes.append(df2)

    # 3. phishing_legit_dataset_KD — 9 categorías de phishing
    print("\n[3/4] phishing_legit_dataset_KD_10000.csv (9 categorias)...")
    df3 = load_dataset(
        DATA_RAW_DIR / "phishing_legit_dataset_KD_10000.csv",
        text_col="text",
        label_col="label",
    )
    print(f"      {len(df3)} registros — phishing: {df3['label'].sum()}, seguro: {(df3['label']==0).sum()}")
    partes.append(df3)

    # 4. Dataset español
    print("\n[4/4] dataset_spanish.csv...")
    df4 = load_dataset(
        DATA_RAW_DIR / "dataset_spanish.csv",
        text_col="text",
        label_col="label",
    )
    print(f"      {len(df4)} registros — phishing: {df4['label'].sum()}, seguro: {(df4['label']==0).sum()}")
    partes.append(df4)

    # Combinar y limpiar
    print("\nCombinando datasets...")
    df = pd.concat(partes, ignore_index=True)
    print(f"Total antes de limpieza: {len(df)}")

    df["text"] = df["text"].astype(str).str.strip()
    df = df.dropna(subset=["text", "label"])
    df = df[df["label"].isin([0, 1])]
    df = df[df["text"].str.len() >= 30]
    df = df[df["text"].str.len() <= 10_000]
    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)

    print(f"Total despues de limpieza: {len(df)}")
    print(f"Phishing: {df['label'].sum()} ({df['label'].mean()*100:.1f}%)")
    print(f"Seguro:   {(df['label']==0).sum()} ({(1-df['label'].mean())*100:.1f}%)")

    df.to_csv(OUTPUT, index=False)
    print(f"\nDataset combinado guardado en: {OUTPUT}")
    print("\nArrancando entrenamiento...")
    print("=" * 60)

    # Ejecutar entrenamiento
    from scripts.train_model import train
    train()


if __name__ == "__main__":
    main()
