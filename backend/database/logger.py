import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "safegen.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp           TEXT,
            input_text          TEXT,
            policy              TEXT,
            role                TEXT,
            malware_score       REAL,
            sensitive_score     REAL,
            intent_score        REAL,
            final_score         REAL,
            decision            TEXT,
            intent_label        TEXT,
            injection_detected  INTEGER,
            malware_type        TEXT,
            severity            TEXT,
            privacy_risk        TEXT,
            anonymisation_score INTEGER,
            input_type          TEXT DEFAULT 'text'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            log_id              INTEGER,
            timestamp           TEXT,
            agreed              INTEGER,
            suggested_decision  TEXT,
            user_comment        TEXT,
            FOREIGN KEY (log_id) REFERENCES logs(id)
        )
    """)
    conn.commit()
    conn.close()

def log_analysis(analysis: dict, input_type: str = "text"):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO logs (
                timestamp, input_text, policy, role,
                malware_score, sensitive_score, intent_score,
                final_score, decision, intent_label,
                injection_detected, malware_type, severity,
                privacy_risk, anonymisation_score, input_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            1 if analysis["intent"]["injection_detected"] else 0,
            analysis["malware"].get("malware_type", "None"),
            analysis["malware"].get("severity", "None"),
            analysis["sensitive"].get("privacy_risk", "None"),
            analysis["sensitive"].get("anonymisation_score", 100),
            input_type
        ))
        log_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        conn.close()
        return log_id
    except Exception as e:
        print(f"Logging error: {e}")
        return None

def log_feedback(log_id: int, agreed: bool, suggested_decision: str = None, user_comment: str = None):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO feedback (log_id, timestamp, agreed, suggested_decision, user_comment)
            VALUES (?, ?, ?, ?, ?)
        """, (
            log_id,
            datetime.now().isoformat(),
            1 if agreed else 0,
            suggested_decision,
            user_comment
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Feedback logging error: {e}")
        return False

def get_logs(limit: int = 50) -> list:
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT l.*, 
                   f.agreed as feedback_agreed,
                   f.suggested_decision as feedback_suggestion
            FROM logs l
            LEFT JOIN feedback f ON f.log_id = l.id
            ORDER BY l.timestamp DESC
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

def get_feedback_stats() -> dict:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute("""
            SELECT
                COUNT(*) as total_feedback,
                SUM(CASE WHEN agreed = 1 THEN 1 ELSE 0 END) as agreed_count,
                SUM(CASE WHEN agreed = 0 THEN 1 ELSE 0 END) as disagreed_count
            FROM feedback
        """)
        row = cursor.fetchone()
        conn.close()
        total = row[0] or 0
        agreed = row[1] or 0
        disagreed = row[2] or 0
        agreement_rate = round((agreed / total * 100) if total > 0 else 0, 1)
        return {
            "total_feedback":   total,
            "agreed_count":     agreed,
            "disagreed_count":  disagreed,
            "agreement_rate":   agreement_rate
        }
    except Exception as e:
        print(f"Error fetching feedback stats: {e}")
        return {}