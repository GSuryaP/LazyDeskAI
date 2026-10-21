"""File organizer engine handling proposed actions, dry-runs, collision avoidance, and execution."""
import shutil
from pathlib import Path
from typing import Dict, Any, List, Tuple
from core.db import log_activity, get_db_connection

def prepare_organization_plan(
    files: List[Dict[str, Any]],
    target_base_dir: str
) -> List[Dict[str, Any]]:
    """
    Generate dry-run proposed actions for scanned files with collision detection.
    """
    base = Path(target_base_dir).expanduser().resolve()
    plan: List[Dict[str, Any]] = []

    for item in files:
        src = Path(item["file_path"])
        suggested_folder = item.get("suggested_folder", item.get("category", "Others"))
        proposed_name = item.get("proposed_name", src.name)

        dest_dir = base / suggested_folder
        dest_path = dest_dir / proposed_name

        collision = False
        collision_resolution = None

        if src == dest_path:
            action_desc = "Keep in place (already in target folder)"
            status = "already_organized"
        elif dest_path.exists():
            collision = True
            # Propose safe collision rename
            stem = Path(proposed_name).stem
            ext = Path(proposed_name).suffix
            counter = 1
            safe_dest = dest_dir / f"{stem}_{counter}{ext}"
            while safe_dest.exists():
                counter += 1
                safe_dest = dest_dir / f"{stem}_{counter}{ext}"
            collision_resolution = safe_dest.name
            action_desc = f"Move and rename to avoid collision ({safe_dest.name})"
            status = "collision_warning"
        else:
            action_desc = f"Move to {suggested_folder}/"
            status = "ready"

        plan.append({
            "id": item.get("id"),
            "file_name": src.name,
            "original_path": str(src),
            "target_dir": str(dest_dir),
            "target_path": str(dest_path),
            "suggested_folder": suggested_folder,
            "file_size": item.get("file_size", 0),
            "category": item.get("category", "Others"),
            "collision": collision,
            "collision_resolution": collision_resolution,
            "action_desc": action_desc,
            "status": status,
            "approved": bool(item.get("approved", 1))
        })

    return plan

def execute_organization_plan(
    plan: List[Dict[str, Any]],
    dry_run: bool = False
) -> Tuple[int, int, List[str]]:
    """
    Execute approved file moves safely with full activity logging for undo.
    """
    success_count = 0
    fail_count = 0
    errors: List[str] = []

    if dry_run:
        # Just count approved items without touching disk
        approved_items = [p for p in plan if p.get("approved") and p.get("status") != "already_organized"]
        return len(approved_items), 0, []

    conn = get_db_connection()

    for item in plan:
        if not item.get("approved"):
            continue
        if item.get("status") == "already_organized":
            continue

        src = Path(item["original_path"])
        dest = Path(item["target_path"])

        if not src.exists():
            fail_count += 1
            err = f"Source file missing: {src.name}"
            errors.append(err)
            continue

        # Handle collision if detected
        if dest.exists() and item.get("collision_resolution"):
            dest = dest.parent / item["collision_resolution"]

        try:
            # Ensure target directory exists
            dest.parent.mkdir(parents=True, exist_ok=True)

            # Move file
            shutil.move(str(src), str(dest))

            # Record in undoable activity log
            log_activity(
                operation_type="organize_move",
                original_path=str(src),
                new_path=str(dest),
                status="success",
                can_undo=True
            )

            # Update DB scanned files status
            if item.get("id"):
                with conn:
                    conn.execute(
                        "UPDATE scanned_files SET status = 'done', file_path = ? WHERE id = ?",
                        (str(dest), item["id"])
                    )

            success_count += 1
        except Exception as e:
            fail_count += 1
            err_msg = f"Failed to move {src.name}: {str(e)}"
            errors.append(err_msg)
            log_activity(
                operation_type="organize_move",
                original_path=str(src),
                new_path=str(dest),
                status="failed",
                error_message=str(e),
                can_undo=False
            )

    conn.close()
    return success_count, fail_count, errors
