import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "safegen.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   TEXT,
            input_text  TEXT,
            policy      TEXT,
            role        TEXT,
            malware_score   REAL,
            sensitive_score REAL,
            intent_score    REAL,
            final_score     REAL,
            decision        TEXT,
            intent_label    TEXT,
            injection_detected INTEGER
        )
    """)
    conn.commit()
    conn.close()

def log_analysis(analysis: dict):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO logs (
                timestamp, input_text, policy, role,
                malware_score, sensitive_score, intent_score,
                final_score, decision, intent_label, injection_detected
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            analysis["original_text"][:500],
            analysis["policy"],
            analysis["role"],
            analysis["malware"]["score"],
            analysis["sensitive"]["score"],
            analysis["intent"]["score"],
            analysis["scoring"]["final_score"],
            analysis["decision"]["decision"],
            analysis["intent"]["label"],
            1 if analysis["intent"]["injection_detected"] else 0
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Logging error: {e}")

def get_logs(limit: int = 50) -> list:
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT * FROM logs
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return []

def get_stats() -> dict:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute("""
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN decision = 'ALLOW'    THEN 1 ELSE 0 END) as allowed,
                SUM(CASE WHEN decision = 'RESTRICT' THEN 1 ELSE 0 END) as restricted,
                SUM(CASE WHEN decision = 'REDACT'   THEN 1 ELSE 0 END) as redacted,
                SUM(CASE WHEN decision = 'BLOCK'    THEN 1 ELSE 0 END) as blocked,
                AVG(final_score) as avg_score
            FROM logs
        """)
        row = cursor.fetchone()
        conn.close()
        return {
            "total":      row[0] or 0,
            "allowed":    row[1] or 0,
            "restricted": row[2] or 0,
            "redacted":   row[3] or 0,
            "blocked":    row[4] or 0,
            "avg_score":  round(row[5] or 0, 2)
        }
    except Exception as e:
        print(f"Error fetching stats: {e}")
        return {}