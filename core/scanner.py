"""File system scanner, metadata extractor, and rule categorizer for LazyDesk AI."""
import hashlib
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from core.config import CATEGORY_MAP
from core.db import get_db_connection

def compute_file_hash(path: Path, max_bytes: int = 1024 * 1024) -> str:
    """Compute MD5 hash of first max_bytes of file for fast comparison."""
    hasher = hashlib.md5()
    try:
        with open(path, "rb") as f:
            chunk = f.read(max_bytes)
            hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""

def compute_full_sha256(path: Path) -> str:
    """Compute full SHA256 for exact duplicate verification."""
    hasher = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return ""

def categorize_file(filename: str) -> str:
    """Determine file category based on extension."""
    ext = Path(filename).suffix.lower()
    for cat, exts in CATEGORY_MAP.items():
        if ext in exts:
            return cat
    return "Others"

def scan_directory(
    dir_path: str,
    max_files: int = 1000,
    recursive: bool = False
) -> List[Dict[str, Any]]:
    """
    Scan a directory, extract metadata, categorize each file,
    and persist results into the database.
    """
    root = Path(dir_path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        return []

    results: List[Dict[str, Any]] = []
    now_iso = datetime.now().isoformat()

    # Collect entries
    files_to_process: List[Path] = []
    try:
        if recursive:
            for p in root.rglob("*"):
                if p.is_file() and not p.name.startswith("."):
                    files_to_process.append(p)
                    if len(files_to_process) >= max_files:
                        break
        else:
            for p in root.iterdir():
                if p.is_file() and not p.name.startswith("."):
                    files_to_process.append(p)
                    if len(files_to_process) >= max_files:
                        break
    except PermissionError:
        return []

    conn = get_db_connection()
    with conn:
        for p in files_to_process:
            try:
                stat = p.stat()
                size = stat.st_size
                mtime = stat.st_mtime
                ext = p.suffix.lower()
                cat = categorize_file(p.name)
                f_hash = compute_file_hash(p)

                # Proposed destination folder based on category
                suggested_folder = cat
                proposed_name = p.name

                item = {
                    "file_path": str(p),
                    "file_name": p.name,
                    "file_ext": ext,
                    "file_size": size,
                    "mtime": mtime,
                    "file_hash": f_hash,
                    "category": cat,
                    "suggested_folder": suggested_folder,
                    "proposed_name": proposed_name,
                    "action": "Move",
                    "status": "pending",
                    "approved": 1,
                    "last_scanned": now_iso
                }
                results.append(item)

                # Insert/replace in DB
                conn.execute("""
                    INSERT INTO scanned_files (
                        file_path, file_name, file_ext, file_size, mtime,
                        file_hash, category, suggested_folder, proposed_name,
                        action, status, approved, last_scanned
                    ) VALUES (
                        :file_path, :file_name, :file_ext, :file_size, :mtime,
                        :file_hash, :category, :suggested_folder, :proposed_name,
                        :action, :status, :approved, :last_scanned
                    )
                    ON CONFLICT(file_path) DO UPDATE SET
                        file_name = excluded.file_name,
                        file_size = excluded.file_size,
                        mtime = excluded.mtime,
                        file_hash = excluded.file_hash,
                        category = excluded.category,
                        suggested_folder = excluded.suggested_folder,
                        last_scanned = excluded.last_scanned;
                """, item)
            except Exception:
                continue

    conn.close()
    return results

def get_scanned_files(status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve scanned files from database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if status_filter:
        cursor.execute("SELECT * FROM scanned_files WHERE status = ? ORDER BY id DESC", (status_filter,))
    else:
        cursor.execute("SELECT * FROM scanned_files ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_file_approval(file_id: int, approved: bool) -> None:
    """Update approval status for a single scanned file."""
    conn = get_db_connection()
    with conn:
        conn.execute("UPDATE scanned_files SET approved = ? WHERE id = ?", (1 if approved else 0, file_id))
    conn.close()

def batch_update_approval(approved: bool) -> None:
    """Update approval for all pending files."""
    conn = get_db_connection()
    with conn:
        conn.execute("UPDATE scanned_files SET approved = ? WHERE status = 'pending'", (1 if approved else 0,))
    conn.close()

def clear_scanned_files() -> None:
    """Clear scanned files cache."""
    conn = get_db_connection()
    with conn:
        conn.execute("DELETE FROM scanned_files;")
    conn.close()
