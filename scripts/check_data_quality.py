"""
Analiza la calidad del dataset antes y despues del preprocesamiento.
Uso: python scripts/check_data_quality.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

raw = pd.read_csv("data/raw/dataset.csv")
processed = pd.read_csv("data/processed/dataset_processed.csv")

print("=" * 55)
print("DATASET RAW (post prepare_dataset.py)")
print("=" * 55)
print(f"Registros            : {len(raw)}")
print(f"Nulos en text        : {raw['text'].isna().sum()}")
vacios = (raw["text"].str.strip() == "").sum()
print(f"Textos vacios        : {vacios}")
dups = raw.duplicated(subset=["text"]).sum()
print(f"Duplicados exactos   : {dups}")
print(f"Longitud minima      : {raw['text'].str.len().min()} chars")
print(f"Longitud maxima      : {raw['text'].str.len().max()} chars")
print(f"Longitud promedio    : {raw['text'].str.len().mean():.0f} chars")

print()
print("=" * 55)
print("DATASET PROCESADO (post preprocess())")
print("=" * 55)
print(f"Registros            : {len(processed)}")
nulos_p = processed["text_clean"].isna().sum()
print(f"Nulos en text_clean  : {nulos_p}")
vacios_p = (processed["text_clean"].str.strip() == "").sum()
print(f"Textos vacios        : {vacios_p}")
print(f"Longitud minima      : {processed['text_clean'].str.len().min()} chars")
print(f"Longitud maxima      : {processed['text_clean'].str.len().max()} chars")
print(f"Longitud promedio    : {processed['text_clean'].str.len().mean():.0f} chars")

print()
print("=" * 55)
print("TEXTOS SOSPECHOSAMENTE CORTOS (< 50 chars procesados)")
print("=" * 55)
cortos = processed[processed["text_clean"].str.len() < 50]
print(f"Cantidad             : {len(cortos)}")
if len(cortos) > 0:
    for _, row in cortos.head(8).iterrows():
        label = "PHISHING" if row["label"] == 1 else "SEGURO"
        print(f"  [{label}] '{row['text_clean']}'")

print()
print("=" * 55)
print("CARACTERES NO ASCII (posibles problemas de encoding)")
print("=" * 55)
non_ascii = raw["text"].apply(
    lambda x: any(ord(c) > 127 for c in str(x))
).sum()
print(f"Registros con chars no-ASCII : {non_ascii} ({round(non_ascii/len(raw)*100,1)}%)")

print()
print("=" * 55)
print("DISTRIBUCION FINAL")
print("=" * 55)
dist = processed["label"].value_counts()
for label, count in dist.items():
    nombre = "Phishing" if label == 1 else "Seguro  "
    pct = round(count / len(processed) * 100, 1)
    bar = "#" * int(pct / 2)
    print(f"  {nombre}: {count:5d} ({pct}%)  {bar}")
