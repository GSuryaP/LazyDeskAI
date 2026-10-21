"""Duplicate detection and safe resolution module for LazyDesk AI."""
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple
from core.scanner import compute_full_sha256
from core.db import log_activity

def find_duplicates(dir_path: str, recursive: bool = True) -> Dict[str, Any]:
    """
    Find exact duplicate files grouped by SHA-256 hash.
    Returns groups of duplicates, total count, and potential storage savings.
    """
    root = Path(dir_path).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        return {"groups": [], "total_duplicates": 0, "potential_savings_bytes": 0}

    # Step 1: Group by file size to quickly filter non-duplicates
    size_map: Dict[int, List[Path]] = {}
    try:
        iterator = root.rglob("*") if recursive else root.iterdir()
        for p in iterator:
            if p.is_file() and not p.name.startswith("."):
                try:
                    sz = p.stat().st_size
                    if sz > 0:  # Skip zero-byte files
                        size_map.setdefault(sz, []).append(p)
                except Exception:
                    continue
    except PermissionError:
        pass

    # Step 2: For sizes with > 1 file, compute full SHA-256
    hash_groups: Dict[str, Dict[str, Any]] = {}
    for sz, file_list in size_map.items():
        if len(file_list) < 2:
            continue
        for p in file_list:
            sha = compute_full_sha256(p)
            if not sha:
                continue
            if sha not in hash_groups:
                hash_groups[sha] = {
                    "hash": sha,
                    "short_hash": sha[:10],
                    "size": sz,
                    "sample_name": p.name,
                    "files": []
                }
            hash_groups[sha]["files"].append({
                "path": str(p),
                "name": p.name,
                "folder": str(p.parent),
                "mtime": p.stat().st_mtime
            })

    # Step 3: Filter groups with >= 2 matching files
    real_duplicates = []
    total_duplicate_copies = 0
    potential_savings = 0

    for sha, group in hash_groups.items():
        if len(group["files"]) >= 2:
            # Sort by creation / mtime so oldest is treated as primary
            group["files"].sort(key=lambda x: x["mtime"])
            group["primary"] = group["files"][0]
            group["duplicates"] = group["files"][1:]
            group["savings"] = group["size"] * len(group["duplicates"])
            potential_savings += group["savings"]
            total_duplicate_copies += len(group["duplicates"])
            real_duplicates.append(group)

    # Sort groups by largest savings first
    real_duplicates.sort(key=lambda g: g["savings"], reverse=True)

    return {
        "groups": real_duplicates,
        "total_duplicates": total_duplicate_copies,
        "potential_savings_bytes": potential_savings
    }

def format_file_size(size_bytes: int) -> str:
    """Format bytes into readable string (KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"

def resolve_duplicates(
    duplicate_paths: List[str],
    action: str = "archive",  # "archive" to _Duplicates_Archive or "delete"
    archive_dir: Optional[str] = None
) -> Tuple[int, List[str]]:
    """
    Safely resolve selected duplicate files.
    All actions are recorded in activity_log for full undoability.
    """
    success_count = 0
    errors = []

    for path_str in duplicate_paths:
        src = Path(path_str)
        if not src.exists():
            continue

        try:
            if action == "archive":
                target_base = Path(archive_dir) if archive_dir else src.parent / "_Duplicates_Archive"
                target_base.mkdir(parents=True, exist_ok=True)
                dest = target_base / src.name
                # Avoid collision in archive folder
                counter = 1
                while dest.exists():
                    dest = target_base / f"{src.stem}_{counter}{src.suffix}"
                    counter += 1

                shutil.move(str(src), str(dest))
                log_activity(
                    operation_type="duplicate_archive",
                    original_path=str(src),
                    new_path=str(dest),
                    status="success",
                    can_undo=True
                )
                success_count += 1

            elif action == "delete":
                # Safe move to a hidden quarantine trash instead of hard unrecoverable unlink
                trash_dir = src.parent / ".lazydesk_quarantine"
                trash_dir.mkdir(parents=True, exist_ok=True)
                dest = trash_dir / f"{src.stem}_{int(src.stat().st_mtime)}{src.suffix}"
                shutil.move(str(src), str(dest))
                log_activity(
                    operation_type="duplicate_quarantine",
                    original_path=str(src),
                    new_path=str(dest),
                    status="success",
                    can_undo=True
                )
                success_count += 1
        except Exception as e:
            errors.append(f"{src.name}: {str(e)}")
            log_activity(
                operation_type="duplicate_resolve_failed",
                original_path=str(src),
                new_path="",
                status="failed",
                error_message=str(e),
                can_undo=False
            )

    return success_count, errors
