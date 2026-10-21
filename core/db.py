"""Database layer for LazyDesk AI using SQLite in WAL mode."""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from core.config import DB_PATH

def get_db_connection() -> sqlite3.Connection:
    """Create a thread-safe connection to SQLite with WAL mode enabled."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def init_db() -> None:
    """Initialize database tables and default settings."""
    conn = get_db_connection()
    with conn:
        # Settings table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
        """)

        # Scanned files table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scanned_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                file_ext TEXT,
                file_size INTEGER,
                mtime REAL,
                file_hash TEXT,
                category TEXT,
                suggested_folder TEXT,
                proposed_name TEXT,
                action TEXT DEFAULT 'Move',
                status TEXT DEFAULT 'pending',
                approved INTEGER DEFAULT 1,
                last_scanned TEXT
            );
        """)

        # Activity / Undo log table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operation_type TEXT NOT NULL,
                original_path TEXT NOT NULL,
                new_path TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                error_message TEXT,
                can_undo INTEGER DEFAULT 1,
                undone_at TEXT
            );
        """)

        # Document intelligence summaries cache
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                file_name TEXT NOT NULL,
                summary TEXT,
                action_items TEXT,
                key_dates TEXT,
                metadata TEXT,
                model_used TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(file_path, file_hash)
            );
        """)

        # Default settings if missing
        conn.execute("""
            INSERT OR IGNORE INTO settings (key, value) VALUES
            ('theme', 'light'),
            ('default_scan_dir', ''),
            ('ollama_host', 'http://localhost:11434'),
            ('preferred_model', 'qwen3:8b'),
            ('dry_run_default', '1'),
            ('auto_backup', '0');
        """)
    conn.close()

def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """Retrieve a setting value by key."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row["value"]
    return default

def set_setting(key: str, value: str) -> None:
    """Store or update a setting value."""
    conn = get_db_connection()
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
    conn.close()

def log_activity(
    operation_type: str,
    original_path: str,
    new_path: str,
    status: str = "success",
    error_message: Optional[str] = None,
    can_undo: bool = True
) -> int:
    """Record an operation in the activity log."""
    conn = get_db_connection()
    now_str = datetime.now().isoformat()
    with conn:
        cur = conn.execute("""
            INSERT INTO activity_log (
                operation_type, original_path, new_path, timestamp, status, error_message, can_undo
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            operation_type, original_path, new_path, now_str, status, error_message, 1 if can_undo else 0
        ))
        row_id = cur.lastrowid
    conn.close()
    return row_id

def get_activity_history(limit: int = 50) -> List[Dict[str, Any]]:
    """Retrieve recent operations chronologically."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM activity_log
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_activity_undone(activity_id: int) -> None:
    """Mark an activity entry as undone."""
    conn = get_db_connection()
    now_str = datetime.now().isoformat()
    with conn:
        conn.execute("""
            UPDATE activity_log
            SET status = 'undone', undone_at = ?, can_undo = 0
            WHERE id = ?
        """, (now_str, activity_id))
    conn.close()

def save_document_summary(
    file_path: str,
    file_hash: str,
    file_name: str,
    summary: str,
    action_items: List[str],
    key_dates: List[str],
    metadata: Dict[str, Any],
    model_used: str
) -> None:
    """Cache document analysis result."""
    conn = get_db_connection()
    now_str = datetime.now().isoformat()
    with conn:
        conn.execute("""
            INSERT OR REPLACE INTO document_summaries (
                file_path, file_hash, file_name, summary, action_items, key_dates, metadata, model_used, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            file_path,
            file_hash,
            file_name,
            summary,
            json.dumps(action_items),
            json.dumps(key_dates),
            json.dumps(metadata),
            model_used,
            now_str
        ))
    conn.close()

def get_document_summary(file_path: str, file_hash: str) -> Optional[Dict[str, Any]]:
    """Fetch cached document analysis if present."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM document_summaries
        WHERE file_path = ? AND file_hash = ?
    """, (file_path, file_hash))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    data = dict(row)
    data["action_items"] = json.loads(data["action_items"] or "[]")
    data["key_dates"] = json.loads(data["key_dates"] or "[]")
    data["metadata"] = json.loads(data["metadata"] or "{}")
    return data

def get_total_documents_summarized() -> int:
    """Get count of documents analyzed."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM document_summaries")
    row = cursor.fetchone()
    conn.close()
    return row["count"] if row else 0
