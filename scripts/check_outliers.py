import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd

df = pd.read_csv("data/raw/dataset.csv")
df["len"] = df["text"].str.len()

print("Distribucion de longitudes (caracteres):")
print(df["len"].describe().round(0).to_string())
print()

umbrales = [1000, 5000, 10000, 50000, 100000]
for u in umbrales:
    n = (df["len"] > u).sum()
    print(f"  Textos con mas de {u:>7} chars: {n}")

print()
print("Top 5 textos mas largos:")
top = df.nlargest(5, "len")[["len", "label"]]
for _, row in top.iterrows():
    label = "PHISHING" if row["label"] == 1 else "SEGURO"
    print(f"  [{label}] {int(row['len']):,} chars")
