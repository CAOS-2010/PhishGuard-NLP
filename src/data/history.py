from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from config.settings import HISTORY_DB


@contextmanager
def _conn():
    con = sqlite3.connect(HISTORY_DB)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def _migrate(con: sqlite3.Connection) -> None:
    """Añade columnas nuevas a tablas existentes sin perder datos."""
    existing = {row[1] for row in con.execute("PRAGMA table_info(analyses)").fetchall()}
    for col, definition in [
        ("urls_found",       "TEXT    DEFAULT ''"),
        ("domain_mismatch",  "INTEGER DEFAULT 0"),
        ("response_time_ms", "REAL    DEFAULT 0"),
    ]:
        if col not in existing:
            con.execute(f"ALTER TABLE analyses ADD COLUMN {col} {definition}")


def init_db() -> None:
    with _conn() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                analyzed_at      TEXT    NOT NULL,
                sender           TEXT,
                subject          TEXT,
                label            TEXT    NOT NULL,
                risk_level       TEXT    NOT NULL,
                confidence       REAL    NOT NULL,
                snippet          TEXT,
                urls_found       TEXT    DEFAULT '',
                domain_mismatch  INTEGER DEFAULT 0,
                response_time_ms REAL    DEFAULT 0
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                registered_at   TEXT    NOT NULL,
                analysis_id     INTEGER,
                text_snippet    TEXT,
                predicted_label TEXT    NOT NULL,
                correct_label   TEXT    NOT NULL,
                confidence      REAL,
                comment         TEXT
            )
        """)
        _migrate(con)


def save_feedback(
    analysis_id: int | None,
    text_snippet: str,
    predicted_label: str,
    correct_label: str,
    confidence: float,
    comment: str = "",
) -> None:
    init_db()
    with _conn() as con:
        con.execute(
            """
            INSERT INTO feedback
                (registered_at, analysis_id, text_snippet, predicted_label,
                 correct_label, confidence, comment)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(timespec="seconds"),
                analysis_id,
                text_snippet[:300],
                predicted_label,
                correct_label,
                confidence,
                comment,
            ),
        )


def get_stats() -> dict:
    init_db()
    with _conn() as con:
        row = con.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN label='phishing' THEN 1 ELSE 0 END) as phishing_count,
                SUM(CASE WHEN label='seguro'   THEN 1 ELSE 0 END) as safe_count,
                AVG(confidence) as avg_confidence,
                AVG(response_time_ms) as avg_response_ms,
                SUM(CASE WHEN risk_level='alto'  THEN 1 ELSE 0 END) as risk_alto,
                SUM(CASE WHEN risk_level='medio' THEN 1 ELSE 0 END) as risk_medio,
                SUM(CASE WHEN risk_level='bajo'  THEN 1 ELSE 0 END) as risk_bajo
            FROM analyses
        """).fetchone()
        daily = con.execute("""
            SELECT
                DATE(analyzed_at) as day,
                COUNT(*) as total,
                SUM(CASE WHEN label='phishing' THEN 1 ELSE 0 END) as phishing,
                SUM(CASE WHEN label='seguro'   THEN 1 ELSE 0 END) as safe
            FROM analyses
            WHERE analyzed_at >= DATE('now', '-30 days')
            GROUP BY day
            ORDER BY day
        """).fetchall()
        fb = con.execute("""
            SELECT
                COUNT(*) as total_feedback,
                SUM(CASE WHEN predicted_label != correct_label THEN 1 ELSE 0 END) as corrections
            FROM feedback
        """).fetchone()

    return {
        "total": row["total"] or 0,
        "phishing_count": row["phishing_count"] or 0,
        "safe_count": row["safe_count"] or 0,
        "avg_confidence": round(float(row["avg_confidence"] or 0), 4),
        "avg_response_ms": round(float(row["avg_response_ms"] or 0), 2),
        "risk_distribution": {
            "alto": row["risk_alto"] or 0,
            "medio": row["risk_medio"] or 0,
            "bajo": row["risk_bajo"] or 0,
        },
        "daily_trend": [
            {"day": r["day"], "total": r["total"], "phishing": r["phishing"], "safe": r["safe"]}
            for r in daily
        ],
        "feedback_total": fb["total_feedback"] or 0,
        "feedback_corrections": fb["corrections"] or 0,
    }


def get_feedback(limit: int = 100) -> list[dict]:
    init_db()
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM feedback ORDER BY registered_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def save_analysis(
    sender: str,
    subject: str,
    label: str,
    risk_level: str,
    confidence: float,
    body_snippet: str,
    urls_found: list[str] | None = None,
    domain_mismatch: bool = False,
    response_time_ms: float = 0.0,
) -> None:
    init_db()
    with _conn() as con:
        con.execute(
            """
            INSERT INTO analyses
                (analyzed_at, sender, subject, label, risk_level, confidence,
                 snippet, urls_found, domain_mismatch, response_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(timespec="seconds"),
                sender,
                subject,
                label,
                risk_level,
                confidence,
                body_snippet[:300],
                json.dumps(urls_found or []),
                int(domain_mismatch),
                round(response_time_ms, 2),
            ),
        )


def count_history() -> int:
    init_db()
    with _conn() as con:
        return con.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]


def get_history(limit: int = 100) -> list[dict]:
    init_db()
    with _conn() as con:
        rows = con.execute(
            "SELECT * FROM analyses ORDER BY analyzed_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def clear_history() -> None:
    init_db()
    with _conn() as con:
        con.execute("DELETE FROM analyses")
