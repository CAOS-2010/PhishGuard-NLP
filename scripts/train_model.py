"""
Ejecutar desde la raíz del proyecto:
    python scripts/train_model.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import joblib
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

from config.settings import (
    ACTIVE_MODEL_FILE,
    CLASSIFIER_RF_FILE,
    CLASSIFIER_SVM_FILE,
    CV_FOLDS,
    MODELS_DIR,
    RANDOM_STATE,
    TEST_SIZE,
    VECTORIZER_FILE,
)
from src.core.classifier import build_rf_pipeline, build_svm_pipeline, save_model
from src.data.loader import clean_raw, load_raw, preprocess_and_save


def train() -> None:
    print("=" * 60)
    print("PhishGuard NLP — Entrenamiento del modelo")
    print("=" * 60)

    print("\n[1/5] Cargando dataset...")
    df = load_raw()
    print(f"      Registros cargados: {len(df)}")
    print(f"      Distribución:\n{df['label'].value_counts().to_string()}")

    print("\n[2/5] Limpieza y preprocesamiento...")
    df = clean_raw(df)
    df = preprocess_and_save(df)
    X = df["text_clean"].tolist()
    y = df["label"].tolist()

    print("\n[3/5] Dividiendo datos (train/test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )
    print(f"      Train: {len(X_train)} | Test: {len(X_test)}")

    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)

    print("\n[4/5] Entrenando modelos...")

    # Random Forest
    print("      [RF] Random Forest...")
    rf_pipeline = build_rf_pipeline()
    rf_cv = cross_val_score(rf_pipeline, X_train, y_train, cv=cv, scoring="recall", n_jobs=-1)
    rf_pipeline.fit(X_train, y_train)
    rf_preds = rf_pipeline.predict(X_test)
    rf_acc = accuracy_score(y_test, rf_preds)
    rf_rec = recall_score(y_test, rf_preds, pos_label=1)
    print(f"         CV Recall (mean): {np.mean(rf_cv):.4f} ± {np.std(rf_cv):.4f}")
    print(f"         Test Accuracy:    {rf_acc:.4f}")
    print(f"         Test Recall:      {rf_rec:.4f}")

    # SVM
    print("      [SVM] LinearSVC...")
    svm_pipeline = build_svm_pipeline()
    svm_cv = cross_val_score(svm_pipeline, X_train, y_train, cv=cv, scoring="recall", n_jobs=-1)
    svm_pipeline.fit(X_train, y_train)
    svm_preds = svm_pipeline.predict(X_test)
    svm_acc = accuracy_score(y_test, svm_preds)
    svm_rec = recall_score(y_test, svm_preds, pos_label=1)
    print(f"         CV Recall (mean): {np.mean(svm_cv):.4f} ± {np.std(svm_cv):.4f}")
    print(f"         Test Accuracy:    {svm_acc:.4f}")
    print(f"         Test Recall:      {svm_rec:.4f}")

    # Select best by Recall (we prioritize not missing phishing)
    if rf_rec >= svm_rec:
        best_pipeline = rf_pipeline
        best_name = "Random Forest"
        best_preds = rf_preds
    else:
        best_pipeline = svm_pipeline
        best_name = "SVM (LinearSVC)"
        best_preds = svm_preds

    print(f"\n      Modelo seleccionado: {best_name}")
    print("\n" + classification_report(y_test, best_preds, target_names=["Seguro", "Phishing"]))

    print("\n[5/5] Guardando modelos...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    save_model(rf_pipeline, CLASSIFIER_RF_FILE)
    save_model(svm_pipeline, CLASSIFIER_SVM_FILE)
    save_model(best_pipeline, ACTIVE_MODEL_FILE)
    joblib.dump(best_pipeline.named_steps["tfidf"], VECTORIZER_FILE)
    print(f"      Modelos guardados en: {MODELS_DIR}")
    print("\n[OK] Entrenamiento completado exitosamente.")


if __name__ == "__main__":
    train()
