"""Duplicate Detection and Safe Resolution interface for LazyDesk AI."""
from pathlib import Path
import streamlit as st
from core.config import APP_DIR
from core.duplicates import find_duplicates, resolve_duplicates, format_file_size
from ui.components import render_top_header, render_metric_card, render_html, render_empty_state

def render_duplicates_view():
    """Render Duplicate Detection and resolution view."""
    render_top_header(
        title="Duplicate Detection",
        description="Identify identical files across folders using cryptographic SHA-256 fingerprinting."
    )

    default_sample_dir = str(APP_DIR / "sample_messy_desktop")
    active_folder = st.session_state.get("active_folder", default_sample_dir)

    # 1. Directory Selector in clean card container
    with st.container(border=True):
        c1, c2, c3 = st.columns([3.4, 1.3, 1.1], vertical_alignment="bottom")
        with c1:
            target_dir = st.text_input("Directory to inspect for duplicates", value=active_folder)
        with c2:
            recursive = st.checkbox("Scan subdirectories", value=True)
        with c3:
            if st.button("Scan Duplicates", type="primary", use_container_width=True):
                st.session_state["active_folder"] = target_dir
                st.rerun()

    resolved_target = Path(target_dir).expanduser().resolve()
    if not resolved_target.is_dir():
        st.error("Specified directory does not exist.")
        return

    # 2. Compute duplicates
    with st.spinner("Calculating SHA-256 signatures for exact matches..."):
        dup_data = find_duplicates(str(resolved_target), recursive=recursive)

    groups = dup_data["groups"]
    total_copies = dup_data["total_duplicates"]
    savings_str = format_file_size(dup_data["potential_savings_bytes"])

    # 3. Summary Metrics
    m1, m2, m3 = st.columns(3)
    with m1:
        render_metric_card("Duplicate Sets", len(groups), "Identical file groups")
    with m2:
        render_metric_card("Redundant Copies", total_copies, "Files that can be safely archived")
    with m3:
        render_metric_card("Reclaimable Storage", savings_str, "Potential space recovery")

    if not groups:
        render_empty_state(
            title="No exact duplicates found",
            message="Every scanned file in this directory has a unique cryptographic fingerprint."
        )
        return

    # 4. Global Safe Resolution Protocol Toolbar
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        act_col1, act_col2, act_col3 = st.columns([2.4, 1.6, 1.8], vertical_alignment="center")

        with act_col1:
            render_html("""
            <div style="font-size: 13.5px; font-weight: 600;">Safe Resolution Protocol</div>
            <div style="font-size: 12px; color: var(--text-secondary);">Redundant copies will be safely archived with complete undo capabilities.</div>
            """)

        with act_col2:
            archive_mode = st.selectbox(
                "Resolution Action",
                ["Safely Move to _Duplicates_Archive", "Move to Quarantine Trash"],
                label_visibility="collapsed"
            )

        with act_col3:
            if st.button("Archive All Redundant Copies", type="primary", use_container_width=True):
                action_code = "archive" if "Archive" in archive_mode else "delete"
                all_dup_paths = []
                for g in groups:
                    for d in g["duplicates"]:
                        all_dup_paths.append(d["path"])

                success_cnt, errors = resolve_duplicates(all_dup_paths, action=action_code)
                if success_cnt > 0:
                    st.success(f"Safely archived {success_cnt} duplicate files. Reclaimed {savings_str}!")
                if errors:
                    st.warning(f"Warnings: {len(errors)} files could not be moved.")
                st.rerun()

    # 5. Grouped Duplicates Detail
    render_html("""
    <div style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px;">
        Duplicate Sets Grouped by SHA-256 Fingerprint
    </div>
    """)

    for i, g in enumerate(groups):
        sample_name = g["sample_name"]
        sz_str = format_file_size(g["size"])
        short_hash = g["short_hash"]
        primary = g["primary"]
        redundant_copies = g["duplicates"]
        group_savings = format_file_size(g["savings"])

        with st.container(border=True):
            render_html(f"""
            <div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 8px;">
                <div style="font-size: 14.5px; font-weight: 600; font-family: var(--font-mono);">{sample_name}</div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <span class="ld-mono" style="font-size: 11px;">SHA-256: {short_hash}...</span>
                    <span class="ld-badge ld-badge-sage">{sz_str} each</span>
                    <span class="ld-badge ld-badge-warn">+{group_savings} recoverable</span>
                </div>
            </div>

            <div style="border-top: 1px solid var(--border); padding-top: 8px; margin-top: 6px;">
                <div style="font-size: 12px; font-weight: 600; color: var(--accent-primary); margin-bottom: 4px;">
                    ✓ Original (Preserved in place):
                </div>
                <div class="ld-mono" style="font-size: 11.5px; padding: 4px 8px; margin-bottom: 10px; display: block;">
                    {primary['path']}
                </div>

                <div style="font-size: 12px; font-weight: 600; color: var(--warning); margin-bottom: 4px;">
                    ⚠ Redundant Copies ({len(redundant_copies)}):
                </div>
            </div>
            """)

            for d in redundant_copies:
                d_col_path, d_col_btn = st.columns([3.8, 1.2], vertical_alignment="center")
                with d_col_path:
                    render_html(f'<div class="ld-mono" style="font-size: 11.5px; padding: 3px 6px;">{d["path"]}</div>')
                with d_col_btn:
                    if st.button("Archive Copy", key=f"res_dup_{i}_{d['name']}", use_container_width=True):
                        resolve_duplicates([d["path"]], action="archive")
                        st.success(f"Archived {d['name']}")
                        st.rerun()
