"""File Organizer interface for LazyDesk AI."""
from pathlib import Path
import streamlit as st
from core.config import APP_DIR, CATEGORY_MAP
from core.scanner import (
    scan_directory,
    get_scanned_files,
    update_file_approval,
    batch_update_approval,
    clear_scanned_files,
)
from core.organizer import prepare_organization_plan, execute_organization_plan
from ui.components import render_top_header, render_html, render_empty_state

def render_organizer_view():
    """Render the File Organizer interface with approvals, dry-run, and collision prevention."""
    render_top_header(
        title="File Organizer",
        description="Inspect, approve, and execute safe categorization and renaming for your workspace."
    )

    default_sample_dir = str(APP_DIR / "sample_messy_desktop")
    active_folder = st.session_state.get("active_folder", default_sample_dir)

    # 1. Folder Controls Card
    with st.container(border=True):
        fc1, fc2, fc3 = st.columns([3.4, 1.2, 1.0], vertical_alignment="bottom")

        with fc1:
            folder_input = st.text_input(
                "Source Directory",
                value=active_folder,
                placeholder="/path/to/folder",
                help="Specify the folder whose files you wish to organize."
            )
        with fc2:
            if st.button("Rescan Folder", type="primary", use_container_width=True):
                target_f = Path(folder_input).expanduser().resolve()
                if target_f.is_dir():
                    with st.spinner("Scanning directory..."):
                        scan_directory(str(target_f))
                        st.session_state["active_folder"] = str(target_f)
                        st.success("Folder scan complete.")
                        st.rerun()
                else:
                    st.error("Directory not found.")
        with fc3:
            if st.button("Clear Cache", use_container_width=True, help="Clear cached scan items"):
                clear_scanned_files()
                st.rerun()

    # 2. Fetch scanned items
    scanned = get_scanned_files()
    if not scanned:
        render_empty_state(
            title="No files currently queued",
            message="Select a folder above and click 'Rescan Folder' to discover unorganized files and generate smart categorization proposals."
        )
        return

    # 3. Search and Category Filters
    filter_col1, filter_col2, filter_col3 = st.columns([2.5, 1.5, 1.2], vertical_alignment="bottom")

    with filter_col1:
        search_query = st.text_input("Search files", placeholder="Filter by name...", label_visibility="collapsed")

    with filter_col2:
        all_categories = ["All Categories"] + list(CATEGORY_MAP.keys()) + ["Others"]
        selected_category = st.selectbox("Category", options=all_categories, label_visibility="collapsed")

    with filter_col3:
        status_filter = st.selectbox("Status", options=["All Statuses", "Pending", "Done"], label_visibility="collapsed")

    # Filter items
    filtered_items = scanned
    if search_query:
        filtered_items = [f for f in filtered_items if search_query.lower() in f["file_name"].lower()]
    if selected_category != "All Categories":
        filtered_items = [f for f in filtered_items if f["category"] == selected_category]
    if status_filter != "All Statuses":
        filtered_items = [f for f in filtered_items if f["status"].lower() == status_filter.lower()]

    # 4. Generate Organization Plan with Collision Detection
    plan = prepare_organization_plan(filtered_items, folder_input)

    # 5. Workflow & Execution Bar
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        ctrl1, ctrl2, ctrl3, ctrl4 = st.columns([1.3, 1.3, 1.6, 2.0], vertical_alignment="center")

        with ctrl1:
            if st.button("Approve All", use_container_width=True):
                batch_update_approval(True)
                st.rerun()

        with ctrl2:
            if st.button("Deselect All", use_container_width=True):
                batch_update_approval(False)
                st.rerun()

        with ctrl3:
            dry_run_enabled = st.checkbox(
                "Dry Run Preview",
                value=st.session_state.get("dry_run_toggle", True),
                help="Simulates moves without touching disk files."
            )
            st.session_state["dry_run_toggle"] = dry_run_enabled

        with ctrl4:
            approved_count = sum(1 for p in plan if p.get("approved") and p.get("status") != "already_organized")
            btn_label = f"Simulate ({approved_count})" if dry_run_enabled else f"Execute Moves ({approved_count})"

            if st.button(btn_label, type="primary", use_container_width=True, disabled=(approved_count == 0)):
                with st.spinner("Processing file operations..."):
                    success_count, fail_count, errors = execute_organization_plan(plan, dry_run=dry_run_enabled)
                    if dry_run_enabled:
                        st.info(f"Dry run preview: {success_count} actions simulated safely. Uncheck 'Dry Run Preview' to apply changes.")
                    else:
                        if success_count > 0:
                            st.success(f"Successfully organized {success_count} files into designated folders.")
                        if fail_count > 0:
                            st.warning(f"{fail_count} operations encountered warnings.")
                        st.rerun()

    # 6. Detailed Proposals List
    render_html(f"""
    <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px;">
        Proposed Operations ({len(plan)} files)
    </div>
    """)

    for item in plan:
        item_id = item.get("id")
        orig_name = item["file_name"]
        suggested_folder = item["suggested_folder"]
        is_collision = item["collision"]
        collision_res = item["collision_resolution"]
        is_approved = item["approved"]
        status = item["status"]

        size_kb = f"{item['file_size'] / 1024:.1f} KB" if item['file_size'] < 1024*1024 else f"{item['file_size'] / (1024*1024):.1f} MB"

        with st.container(border=True):
            r_check, r_details, r_badge = st.columns([0.4, 4.2, 1.4], vertical_alignment="center")

            with r_check:
                new_app = st.checkbox(f"Select {orig_name}", value=is_approved, key=f"app_check_{item_id}", label_visibility="collapsed")
                if new_app != is_approved:
                    update_file_approval(item_id, new_app)
                    st.rerun()

            with r_details:
                collision_warning_html = f'<span class="ld-badge ld-badge-warn" style="margin-left: 8px;">Collision: Will rename to {collision_res}</span>' if is_collision else ''
                render_html(f"""
                <div style="display: flex; align-items: baseline; gap: 8px;">
                    <span style="font-family: var(--font-mono); font-weight: 600; font-size: 13.5px;">{orig_name}</span>
                    <span style="font-size: 12px; color: var(--text-secondary);">({size_kb})</span>
                </div>
                <div style="font-size: 12.5px; color: var(--text-secondary); margin-top: 3px;">
                    <span>→ Destination: </span>
                    <span class="ld-mono" style="font-size: 11.5px;">{suggested_folder}/</span>
                    {collision_warning_html}
                </div>
                """)

            with r_badge:
                if status == "already_organized":
                    badge_html = '<span class="ld-badge">Organized</span>'
                elif is_collision:
                    badge_html = '<span class="ld-badge ld-badge-warn">Needs Rename</span>'
                else:
                    badge_html = '<span class="ld-badge ld-badge-sage">Ready to Move</span>'
                render_html(f'<div style="text-align: right;">{badge_html}</div>')
