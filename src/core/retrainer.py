from __future__ import annotations

import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import Callable

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent.parent

_is_training = False
_last_trained_at: str | None = None
_examples_added = 0
_last_error: str | None = None
_lock = threading.Lock()


def get_status() -> dict:
    with _lock:
        return {
            "is_training": _is_training,
            "last_trained_at": _last_trained_at,
            "examples_added": _examples_added,
            "error": _last_error,
        }


def _add_to_dataset(text: str, correct_label: str) -> bool:
    data_path = ROOT / "data" / "raw" / "dataset.csv"
    try:
        df = pd.read_csv(data_path)
        text_clean = text.strip()
        if text_clean in df["text"].str.strip().values:
            return False
        label_int = 1 if correct_label == "phishing" else 0
        new_row = pd.DataFrame([{"text": text_clean, "label": label_int}])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(data_path, index=False)
        return True
    except Exception:
        return False


def _run_training(reload_fn: Callable) -> None:
    global _is_training, _last_trained_at, _last_error
    try:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "train_model.py")],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
        )
        if result.returncode != 0:
            with _lock:
                _is_training = False
                _last_error = result.stderr[-500:] if result.stderr else "Error desconocido"
            return

        reload_fn()

        with _lock:
            _is_training = False
            _last_trained_at = datetime.now().isoformat(timespec="seconds")
            _last_error = None
    except Exception as exc:
        with _lock:
            _is_training = False
            _last_error = str(exc)


def trigger_retrain(text: str, correct_label: str, reload_fn: Callable) -> bool:
    """Agrega el ejemplo al dataset y lanza reentrenamiento en segundo plano."""
    global _is_training, _examples_added
    with _lock:
        if _is_training:
            return False

    added = _add_to_dataset(text, correct_label)
    if not added:
        return False

    with _lock:
        _is_training = True
        _examples_added += 1

    threading.Thread(target=_run_training, args=(reload_fn,), daemon=True).start()
    return True
