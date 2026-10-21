"""Overview Dashboard and Guided Presentation Tour for LazyDesk AI."""
from pathlib import Path
import streamlit as st
from core.config import APP_DIR
from core.db import get_activity_history, get_total_documents_summarized
from core.duplicates import find_duplicates
from core.llm_service import LLMService
from core.scanner import scan_directory, get_scanned_files
from ui.components import render_top_header, render_metric_card, render_html, navigate_to

def render_overview_view():
    """Render the primary Overview presentation dashboard and guided tour."""
    render_top_header(
        title="Overview",
        description="A calm overview of your local workspace files and automated sorting."
    )

    default_sample_dir = str(APP_DIR / "sample_messy_desktop")
    current_scan_dir = st.session_state.get("active_folder", default_sample_dir)

    # 1. Presentation Hero Brief
    with st.container(border=True):
        render_html("""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <span class="ld-badge ld-badge-sage" style="font-size: 11px; padding: 3px 8px;">
                🦥 Hacktoberfest 2026: Slow &amp; Steady
            </span>
            <span class="ld-badge" style="font-size: 11px;">
                Powered by Google Gemma 2
            </span>
        </div>
        <div style="font-size: 1.45rem; font-weight: 600; margin-bottom: 6px; color: var(--text-primary); letter-spacing: -0.02em;">
            A little less to do.
        </div>
        <div style="color: var(--text-secondary); font-size: 13.5px; max-width: 760px; line-height: 1.6; margin-bottom: 6px;">
            Channel your inner sloth. LazyDesk AI is a calm, local-first productivity assistant that automates the computer chores you keep putting off. Automatically sort messy downloads, extract executive summaries and deadlines with local <strong>Google Gemma 2</strong>, and fingerprint exact duplicates—with 100% air-gapped privacy and zero cloud fees.
        </div>
        """)

    # 2. Guided 3-Step Feature Tour (Leads directly to content pages)
    render_html("""
    <div style="font-size: 11.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin: 16px 0 10px 0;">
        Explore Capabilities &amp; Workspaces
    </div>
    """)

    tour_col1, tour_col2, tour_col3 = st.columns(3)

    with tour_col1:
        with st.container(border=True):
            render_html("""
            <div style="font-size: 14.5px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">
                📂 File Organizer
            </div>
            <div style="font-size: 12.5px; color: var(--text-secondary); line-height: 1.5; min-height: 54px; margin-bottom: 12px;">
                Categorizes clutter into Documents, Code, Images, and Archives with dry-run previews and collision detection.
            </div>
            """)
            if st.button("Launch Organizer →", key="tour_btn_organizer", use_container_width=True):
                navigate_to("File Organizer")

    with tour_col2:
        with st.container(border=True):
            render_html("""
            <div style="font-size: 14.5px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">
                🧠 Document Intelligence
            </div>
            <div style="font-size: 12.5px; color: var(--text-secondary); line-height: 1.5; min-height: 54px; margin-bottom: 12px;">
                Reads PDFs and notes using Google Gemma 2, distilling executive briefs, action items, and milestone dates.
            </div>
            """)
            if st.button("Open Document Reader →", key="tour_btn_doc", use_container_width=True):
                navigate_to("Document Intelligence")

    with tour_col3:
        with st.container(border=True):
            render_html("""
            <div style="font-size: 14.5px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">
                🛡 Deduplication &amp; Undo
            </div>
            <div style="font-size: 12.5px; color: var(--text-secondary); line-height: 1.5; min-height: 54px; margin-bottom: 12px;">
                Identifies identical files with cryptographic SHA-256 fingerprints, reclaims space safely, and provides disk undo.
            </div>
            """)
            if st.button("Inspect Duplicates →", key="tour_btn_dup", use_container_width=True):
                navigate_to("Duplicates")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 3. Source Directory Quick Scanner Card
    with st.container(border=True):
        scan_col1, scan_col2 = st.columns([3.4, 1.2], vertical_alignment="bottom")
        with scan_col1:
            folder_to_scan = st.text_input(
                "Source Directory to Scan",
                value=current_scan_dir,
                placeholder="/path/to/folder or /home/username/Downloads",
                help="Enter any directory on your computer to scan and organize."
            )
        with scan_col2:
            if st.button("Scan Folder", type="primary", use_container_width=True):
                target_p = Path(folder_to_scan).expanduser().resolve()
                if target_p.is_dir():
                    with st.spinner("Scanning directory..."):
                        results = scan_directory(str(target_p))
                        st.session_state["active_folder"] = str(target_p)
                        st.session_state["last_scanned_count"] = len(results)
                        st.success(f"Scanned {len(results)} files in {target_p.name}")
                        st.rerun()
                else:
                    st.error("Directory does not exist or is not accessible.")

    # 4. Four Compact Metric Areas
    scanned_items = get_scanned_files()
    total_scanned = len(scanned_items)
    pending_suggestions = sum(1 for f in scanned_items if f.get("status") == "pending")

    # Compute duplicates count
    duplicate_info = {"total_duplicates": 0, "potential_savings_bytes": 0}
    current_p = Path(current_scan_dir).expanduser().resolve()
    if current_p.is_dir():
        duplicate_info = find_duplicates(str(current_p), recursive=False)

    total_summaries = get_total_documents_summarized()

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        render_metric_card("Files Scanned", total_scanned, f"In {Path(current_scan_dir).name}")
    with m2:
        render_metric_card("Suggestions", pending_suggestions, "Awaiting approval")
    with m3:
        render_metric_card("Duplicates", duplicate_info["total_duplicates"], f"{duplicate_info['potential_savings_bytes'] / (1024*1024):.1f} MB potential")
    with m4:
        render_metric_card("Summarized", total_summaries, "Documents indexed")

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # 5. Two-Column Layout: Pending Actions & Local AI Status
    left_col, right_col = st.columns([1.8, 1.2])

    with left_col:
        render_html("""
        <div style="font-size: 11.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px;">
            Pending Organization Actions
        </div>
        """)

        pending_items = [f for f in scanned_items if f.get("status") == "pending"]
        if pending_items:
            table_rows = ""
            for item in pending_items[:4]:
                name = item['file_name']
                cat = item['category']
                table_rows += f"""<tr>
<td style="font-family: var(--font-mono); font-size: 12px; font-weight: 500;">{name}</td>
<td><span class="ld-badge ld-badge-sage">{cat}</span></td>
<td style="color: var(--text-secondary); font-size: 12px;">Move to {cat}/</td>
</tr>"""

            render_html(f"""
            <table class="ld-table">
                <thead>
                    <tr>
                        <th>File Name</th>
                        <th>Category</th>
                        <th>Suggested Action</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            """)

            if st.button("Review All Suggestions in Organizer →", key="review_pending_btn", use_container_width=True):
                navigate_to("File Organizer")
        else:
            with st.container(border=True):
                render_html("""
                <div style="text-align: center; padding: 16px 12px;">
                    <div style="font-weight: 600; font-size: 14px; margin-bottom: 4px; color: var(--text-primary);">Workspace is tidy</div>
                    <div style="color: var(--text-secondary); font-size: 13px;">No pending file moves. Click 'Scan Folder' above to analyze your directory.</div>
                </div>
                """)

    with right_col:
        render_html("""
        <div style="font-size: 11.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px;">
            Local AI Engine Status
        </div>
        """)

        llm = LLMService()
        connected, models, status_msg, latency = llm.check_connection()
        preferred = llm.get_preferred_model()

        dot = "ld-dot-green" if connected else "ld-dot-amber"
        conn_text = "Operational" if connected else "Unreachable"

        with st.container(border=True):
            render_html(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <div style="font-size: 13px; font-weight: 600;">Ollama Engine</div>
                <div style="display: flex; align-items: center; gap: 6px; font-size: 12px;">
                    <span class="ld-dot {dot}"></span>
                    <span>{conn_text}</span>
                </div>
            </div>
            <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">Active Model:</div>
            <div class="ld-mono" style="margin-bottom: 12px; display: inline-block;">{preferred}</div>
            
            <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--text-secondary); border-top: 1px solid var(--border); padding-top: 8px;">
                <span>Inference Latency</span>
                <span>{latency} ms</span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 12px; color: var(--text-secondary); margin-top: 4px; margin-bottom: 10px;">
                <span>Available Models</span>
                <span>{len(models)} installed</span>
            </div>
            """)

            if st.button("Configure Engine in Settings →", key="overview_settings_btn", use_container_width=True):
                navigate_to("Settings")

    # 6. Recent Activity Section
    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    render_html("""
    <div style="font-size: 11.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-secondary); margin-bottom: 8px;">
        Recent Activity
    </div>
    """)

    history = get_activity_history(limit=4)
    if history:
        rows = ""
        for h in history:
            op = h["operation_type"].replace("_", " ").title()
            orig = Path(h["original_path"]).name
            target = Path(h["new_path"]).name if h["new_path"] else "-"
            st_badge = "ld-badge-sage" if h["status"] == "success" else "ld-badge-warn"
            rows += f"""<tr>
<td style="font-weight: 500;">{op}</td>
<td class="ld-mono" style="font-size: 12px;">{orig}</td>
<td class="ld-mono" style="font-size: 12px;">{target}</td>
<td><span class="ld-badge {st_badge}">{h['status'].title()}</span></td>
</tr>"""

        render_html(f"""
        <table class="ld-table">
            <thead>
                <tr>
                    <th>Operation</th>
                    <th>Source File</th>
                    <th>Target Destination</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        """)
    else:
        with st.container(border=True):
            render_html("""
            <div style="text-align: center; font-size: 13px; color: var(--text-secondary); padding: 8px 0;">
                No file movements recorded yet. Files organized will appear here with full undo capabilities.
            </div>
            """)
