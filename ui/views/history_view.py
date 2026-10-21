"""Activity History and Physical File Undo interface for LazyDesk AI."""
from pathlib import Path
import streamlit as st
from core.history import list_recent_activities, undo_operation
from ui.components import render_top_header, render_html, render_empty_state

def render_history_view():
    """Render Activity History and functional Undo control."""
    render_top_header(
        title="Activity History",
        description="A transactional record of all file movements, archivals, and changes with physical disk undo."
    )

    activities = list_recent_activities(limit=100)

    if not activities:
        render_empty_state(
            title="No activity logged yet",
            message="Every file moved, renamed, or archived by LazyDesk is tracked here. You can undo any action at any time."
        )
        return

    # Header stats
    total_ops = len(activities)
    success_ops = sum(1 for a in activities if a["status"] == "success")
    undone_ops = sum(1 for a in activities if a["status"] == "undone")

    render_html(f"""
    <div style="display: flex; gap: 16px; margin-bottom: 14px; font-size: 13px; color: var(--text-secondary);">
        <div><strong>Total logged operations:</strong> {total_ops}</div>
        <div><strong>Active:</strong> {success_ops}</div>
        <div><strong>Reversed (Undone):</strong> {undone_ops}</div>
    </div>
    """)

    # Activity list
    for act in activities:
        act_id = act["id"]
        op_type = act["operation_type"].replace("_", " ").title()
        orig_path = act["original_path"]
        new_path = act["new_path"]
        timestamp = act["timestamp"]
        status = act["status"]
        can_undo = act["can_undo"] and status == "success"
        error_msg = act["error_message"]

        formatted_time = timestamp.replace("T", " ")[:19]

        with st.container(border=True):
            col_main, col_action = st.columns([4.0, 1.4], vertical_alignment="center")

            with col_main:
                status_badge = "ld-badge-sage" if status == "success" else ("ld-badge" if status == "undone" else "ld-badge-error")
                error_html = f"<div style='color: var(--error); margin-top: 4px;'><strong>Error:</strong> {error_msg}</div>" if error_msg else ""
                dest_html = f"<div><strong>Destination:</strong> <span class='ld-mono'>{new_path}</span></div>" if new_path else ""

                render_html(f"""
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
                    <span style="font-weight: 600; font-size: 14px; color: var(--text-primary);">{op_type}</span>
                    <span class="ld-badge {status_badge}">{status.title()}</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">{formatted_time}</span>
                </div>
                <div style="font-size: 12.5px; color: var(--text-secondary); line-height: 1.5;">
                    <div><strong>Original:</strong> <span class="ld-mono">{orig_path}</span></div>
                    {dest_html}
                    {error_html}
                </div>
                """)

            with col_action:
                if can_undo:
                    if st.button("↩ Undo Move", key=f"undo_btn_{act_id}", use_container_width=True, help="Physically move file back to original path on disk"):
                        with st.spinner("Restoring file to original path..."):
                            success, message = undo_operation(act_id)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
                            st.rerun()
                elif status == "undone":
                    render_html('<div style="text-align: right; font-size: 12px; color: var(--text-secondary);">Restored to origin</div>')
                else:
                    render_html('<div style="text-align: right; font-size: 12px; color: var(--text-secondary);">Non-reversible</div>')
