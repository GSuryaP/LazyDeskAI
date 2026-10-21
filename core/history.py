"""Activity history management and physical file undo engine."""
import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple
from core.db import get_activity_history, mark_activity_undone, get_db_connection

def list_recent_activities(limit: int = 50) -> List[Dict[str, Any]]:
    """Get recent activity entries."""
    return get_activity_history(limit=limit)

def undo_operation(activity_id: int) -> Tuple[bool, str]:
    """
    Physically reverse an operation by moving the file back to its original location.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM activity_log WHERE id = ?", (activity_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return False, "Activity record not found."

    activity = dict(row)

    if not activity["can_undo"]:
        return False, "This action has already been undone or cannot be reversed."

    if activity["status"] != "success":
        return False, "Only successful operations can be undone."

    current_path = Path(activity["new_path"])
    original_path = Path(activity["original_path"])

    if not current_path.exists():
        return False, f"File no longer exists at '{current_path}'. It may have been moved or deleted manually."

    # Ensure original parent directory exists
    original_path.parent.mkdir(parents=True, exist_ok=True)

    # Check collision at original path
    if original_path.exists() and original_path != current_path:
        # Move with collision suffix
        stem = original_path.stem
        ext = original_path.suffix
        counter = 1
        safe_orig = original_path.parent / f"{stem}_restored_{counter}{ext}"
        while safe_orig.exists():
            counter += 1
            safe_orig = original_path.parent / f"{stem}_restored_{counter}{ext}"
        target_restore = safe_orig
        message_note = f" (restored as '{safe_orig.name}' due to filename collision)"
    else:
        target_restore = original_path
        message_note = ""

    try:
        shutil.move(str(current_path), str(target_restore))
        mark_activity_undone(activity_id)
        return True, f"Successfully restored '{current_path.name}' back to '{target_restore}'{message_note}."
    except Exception as e:
        return False, f"Failed to undo operation: {str(e)}"
